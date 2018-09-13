class Filter:

    def __init__(self, args):
        self.filter_namespace = []
        self.filter_name = []
        self.filter_label = []

        for fdef in args.filters:
            if fdef.startswith('@'):
                self.filter_namespace.append(fdef[1:])
            elif fdef.startswith('~'):
                self.filter_name.append(fdef[1:])
            elif '~' in fdef:
                self.filter_label.append(fdef.split('~', 2))
            else:
                raise ValueError('Unknow filter definition %s', fdef)

    def check(self, metadata):
        # namespace
        for fdef in self.filter_namespace:
            if fdef == metadata.namespace:
                break
        else:
            if self.filter_namespace != []:
                return False
        # name
        for fdef in self.filter_name:
            if fdef not in metadata.name:
                return False
        # label
        for fdef in self.filter_label:
            if fdef[0] not in metadata.labels or fdef[1] not in metadata.labels[fdef[0]]:
                return False
        return True
