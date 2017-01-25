from propertymappingbase import DashboardPropertyMapperBase, DashboardProperty

class DashboardBase(object):
    def __init__(self, name, template, group = None, mapping=None):
        self.name = name
        self.group = group
        self.template = template
        self.mapping = []
        self.mapping_by_name = {}
        if mapping != None:
            for m in mapping:
                self.addMapping(m)

        self.instance = None

    def setInstanceObject(self, o):
        self.instance = o

    def addMapping(self, m):
        if m == None:
            raise Exception("No mapping provided!")

        try:
            if not isinstance(m, DashboardPropertyMapperBase):
                raise Exception ("Invalid mapping objects provided!")
            self.mapping_by_name[m.name] = m
            self.mapping.append(m)
        except:
            raise Exception("An invalid mapping list was provided!")


    def setParameters(self, params):
        for k, v in params.iteritems():
            try:
                mapping = self.mapping_by_name[k]
            except:
                raise("Invalid mapping \"%s\"!" % k)

            try:
                if isinstance(mapping, DashboardProperty):
                    #it is a property (already containing a reference to the object)
                    mapping.set_commit_value_from_string(v)
                else:
                    #it is a property mapping. Use the instance.
                    mapping.set_commit_value_from_string(v, self.instance)
            except Exception as e:
                raise ("Failed to set the value (%s)!" % str(e))

    def validate(self):
        pass

    def reset(self):
        for m in self.mapping:
            m.reset()

    def commit(self):
        for m in self.mapping:
            m.commit()

    def getTemplate(self):
        return self.template
