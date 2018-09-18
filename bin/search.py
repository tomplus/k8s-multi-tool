#! /usr/bin/env python

import asyncio
import argparse
import re

from kubernetes_asyncio import client, config
from kubernetes_asyncio.stream import WsApiClient

from k8smtool import Filter, Table


class Cmd:

    def __init__(self):
        self.filter = None
        self.args = None

    def arg_parse(self):
        parser = argparse.ArgumentParser(description='Search objects')
        parser.add_argument('query', type=str,
                            help="regexp pattern")
        parser.add_argument('filters', type=str, nargs="*",
                            help="@namespace, ~name, label-name~value")

        self.args = parser.parse_args()
        self.filter = Filter(self.args)

    def list_obj_mapping(self):
        obj_map = {}
        v1 = client.CoreV1Api()
        for method in dir(v1):
            rer = re.search(r'^list_(.*)_for_all_namespaces$', method)
            if rer is not None and method != 'list_event_for_all_namespaces':
                obj_map[rer.group(1)] = getattr(v1, method)
        return obj_map

    async def search(self):

        query = '.{0,10}' + self.args.query + '.{0,10}'

        obj_map = self.list_obj_mapping()
        tab = Table()
        tab.add('NAMESPACE', 'TYPE', 'OBJECT', 'RESULT')

        for obj_type, obj_query in obj_map.items():
            ret = await obj_query()
            for obj in ret.items:
                if self.filter.check(obj.metadata):
                    match_result = re.search(query, str(obj))
                    if match_result is not None:
                        tab.add(obj.metadata.namespace,
                                obj_type,
                                obj.metadata.name,
                                match_result.group(0).strip())
        tab.print()


async def main():
    cmd = Cmd()
    cmd.arg_parse()
    await config.load_kube_config()
    await cmd.search()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
