#! /usr/bin/env python

import asyncio
import argparse

from kubernetes_asyncio import client, config
from kubernetes_asyncio.stream import WsApiClient

from k8smtool import Filter, Table


class Cmd:

    def __init__(self):
        self.filter = None
        self.args = None

    def arg_parse(self):
        parser = argparse.ArgumentParser(description='Execute actions on pods')

        commands = [name[3:].replace('_', '-')
                    for name in dir(self) if name.startswith('do_')]
        parser.add_argument('command', choices=commands,
                            help="command to execute")

        parser.add_argument('filters', type=str, nargs="*",
                            help="@namespace, ~name, label-name~value")

        group = parser.add_argument_group('Option for `exec` command:')
        group.add_argument('--cmd', type=str,
                           help="command to execute")
        group.add_argument('--batch-size', type=int,
                           help="batch size")

        group = parser.add_argument_group('Option for `tail` command:')
        group.add_argument('--follow', action="store_true",
                           help="follow logs")
        group.add_argument('--lines', type=int, default=10,
                           help="show the last lines")

        self.args = parser.parse_args()
        self.filter = Filter(self.args)

    async def list_pods(self, check_cond):
        v1 = client.CoreV1Api()
        ret = await v1.list_pod_for_all_namespaces()
        pods = []
        tab = Table()
        tab.add('NAMESPACE', 'PODS', 'VERSION', 'STATUS', 'CONDITIONS', 'NODE')
        for pod in ret.items:
            if self.filter.check(pod.metadata):
                conds = [
                    cond.type for cond in pod.status.conditions if 'T' in cond.status]
                if pod.metadata.deletion_timestamp is not None:
                    conds.append('Terminating')
                if check_cond(conds):
                    conds_txt = '+'.join(sorted(conds))
                    vers = [container.image.split(
                        ':')[-1] if ':' in container.image else 'latest' for container in pod.spec.containers]
                    vers_txt = ';'.join(vers)
                    tab.add(pod.metadata.namespace, pod.metadata.name, vers_txt,
                            pod.status.phase, conds_txt, pod.spec.node_name)

                    pods.append(pod)
        tab.print()
        return pods

    async def do(self):
        await getattr(self, 'do_' + self.args.command.replace('-', '_'))()

    async def do_ls(self):
        await self.list_pods(lambda _: True)

    async def do_delete_broken(self):

        to_delete = await self.list_pods(lambda conds: 'Ready' not in conds)
        confirm = input('Do you want to delete these pods [YES/NO]?')
        if confirm == 'YES':
            for i, pod in enumerate(to_delete):
                pod_namespace = pod.metadata.namespace
                pod_name = pod.metadata.name
                print('{}/{} {}/{} deleting...'.format(i+1,
                                                       len(to_delete), pod_namespace, pod_name))
                await v1.delete_namespaced_pod(pod_name, pod_namespace, client.V1DeleteOptions())

    async def do_exec(self):

        to_exec = await self.list_pods(lambda conds: 'Ready' in conds)
        if not self.args.cmd:
            self.args.cmd = input('Enter a command to execut (or use --exec):')
            if not self.args.cmd:
                return
        else:
            print('Execute command {}'.format(self.args.cmd))

        v1_ws = client.CoreV1Api(api_client=WsApiClient())
        batch = []
        for i, pod in enumerate(to_exec):
            pod_namespace = pod.metadata.namespace
            pod_name = pod.metadata.name
            pod_container = pod.status.container_statuses[0].name
            print('{}/{} {}/{} sending command'.format(i +
                                                       1, len(to_exec), pod_namespace, pod_name))

            async def __exec_and_print(pod_name, pod_namespace, pod_container):
                call = await v1_ws.connect_get_namespaced_pod_exec(pod_name, pod_namespace,
                                                                   container=pod_container,
                                                                   command=self.args.cmd,
                                                                   stderr=True,
                                                                   stdin=False,
                                                                   stdout=True,
                                                                   tty=False)
                print('Response from {}/{}\n{}\n'.format(pod_namespace, pod_name, call))

            batch.append(__exec_and_print(
                pod_name, pod_namespace, pod_container))

            if self.args.batch_size is not None and len(batch) >= self.args.batch_size:
                await asyncio.wait(batch)
                batch = []

        if batch:
            await asyncio.wait(batch)

    async def do_tail(self):
        pods = await self.list_pods(lambda _: True)
        pod_cmd = []

        async def print_pod_logs(name, namespace, container, lines, follow):
            v1 = client.CoreV1Api()
            resp = await v1.read_namespaced_pod_log(name,
                                                    namespace,
                                                    container=container,
                                                    tail_lines=lines,
                                                    follow=follow,
                                                    _preload_content=not follow)

            if not follow:
                print('{}/{}\n{}\n'.format(namespace, name, resp))
            else:
                while True:
                    line = await resp.content.readline()
                    if not line:
                        break
                    print("{}/{}: {}".format(namespace, name,
                                             line.decode('utf-8')), end="")

        for pod in pods:
            for container in pod.spec.containers:
                pod_cmd.append(print_pod_logs(pod.metadata.name,
                                              pod.metadata.namespace,
                                              container.name,
                                              self.args.lines,
                                              self.args.follow))

        await asyncio.wait(pod_cmd)

    async def do_images(self):
        v1 = client.CoreV1Api()
        ret = await v1.list_pod_for_all_namespaces()

        tab = Table()
        tab.add('IMAGE', 'NAMESACE', 'POD-STATUS')
        for pod in ret.items:
            if self.filter.check(pod.metadata):
                for container in pod.spec.containers:
                    tab.add(container.image, pod.metadata.namespace,
                            pod.status.phase)

        tab.print(distinct=True)


async def main():
    cmd = Cmd()
    cmd.arg_parse()
    await config.load_kube_config()
    await cmd.do()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
