class Node():
    def __init__(self):
        self.name = None # node name
        self.data = None # data string
        self.attribute = None # attribute dictionary
        self.child = None # child node list
        self.parent = None # parent node
        self.is_contain = None # boolean, tag contain data
        
        self.open_tag_scope = None # open tag start, end position
        self.close_tag_scope = None # close tag start, end position
        self.data_scope = None # data start, end position
    
    def __str__(self):
        p = self.parent.name if not self.parent is None else "-"
        c = self.child if not self.child is None else "-"
        n = self.name
        return "name : {0}, parent : {1}, child : {2}".format(n,p,c)

    
    def parse_open_tag(self, stream, start, end):
        tag_start = stream.find("<", start, end)
        tag_end1, tag_end2 = stream.find(">", tag_start, end), stream.find("/>", tag_start, end)
        tag_end = -1
        # check tag string
        if tag_start == -1 or (tag_end1 == -1 and tag_end2 == -1):
            return None
        # check tag form is contain data or not
        if (tag_end1 == -1 or tag_end2 == -1):
            self.is_contain = False if tag_end2 == -1 else True
            tag_end = tag_end1 + 1 if tag_end2 == -1 else tag_end2 + 2
        else:
            self.is_contain = False if tag_end1 < tag_end2 else True
            self.is_contain = tag_end1 + 1 if tag_end1 < tag_end2 else tag_end2 + 2
        # save the position
        self.open_tag_scope = (tag_start, tag_end)
        # get open tag data
        tag_data = stream[tag_start:tag_end]
        tag_data = tag_data.lstrip('<').rstrip('/>').rstrip('>')
        tag_data = tag_data.split(" ")
        # get name
        self.name = tag_data[0]
        tag_data = tag_data[1:]
        attribute_data = dict()
        # get attributes
        for d in tag_data:
            t = d.split("=")
            k, v = t[0], t[1]
            v = v.strip("\"")
            attribute_data[k] = v
        if attribute_data: # dictionaory is not empty
            self.attribute = attribute_data
        return True
    
    def parse_close_tag(self, stream, end):
        tag_start = stream.find("</{0}>".format(self.name), self.open_tag_scope[1], end)
        if tag_start == -1:
            return None
        self.close_tag_scope = (tag_start, tag_start + len("</{0}>".format(self.name)))
        return True
    
    def parse_data(self, stream):
        self.data_scope = (self.open_tag_scope[1],self.close_tag_scope[0])
        return (self.open_tag_scope[1],self.close_tag_scope[0])


if __name__ == "__main__":
    
    stream = None
    root = Node()
    current = root
    file_path = "D:\\lab\\xml_parser\\data\\test2.xml"
    with open(file_path, 'r', encoding='UTF8') as f:
    stream = f.read()

    # parse XML tree
    try:
        if stream is None:
            raise Exception("file read error")
        # 1. check xml declaration, control parse range.
        declaration_start, declaration_end = stream.find("<?"), stream.find("?>")
        if declaration_start == -1 or declaration_end == -1:
            raise Exception("xml declaration not found")
        parse_start, parse_end = declaration_end + len("?>"), len(stream)
        
        while True:
            # 2. find open tag, close tag, data
            if current.parse_open_tag(stream, parse_start, parse_end) is None:
                raise Exception("open tag not found or parse open tag error")
            if current.parse_close_tag(stream, parse_end) is None:
                raise Exception("close tag not found")
            current.parse_data(stream)
            print(current)
            # 3. find child node
            if stream.find("<", current.data_scope[0], current.data_scope[1]) != -1:
                # create child node
                child_node = Node()
                # save parent node address
                child_node.parent = current
                # save child node address
                if current.child is None:
                    current.child = []
                current.child.append(child_node)
                # change current node, change parse scope
                parse_start, parse_end = current.data_scope[0], current.data_scope[1]
                current = child_node
                continue
            else:
                # save data to current node
                current.data = stream[current.data_scope[0]:current.data_scope[1]].strip()
            # 4. find brother node
            if current.parent is None:
                break
            traverse_end = 0
            for children in current.parent.child:
                if traverse_end < children.close_tag_scope[1]:
                    traverse_end = children.close_tag_scope[1]
            # if not find any node, move to parent node and find parent's brother
            if stream.find("<", traverse_end, current.parent.data_scope[1]) == -1:
                # if parent node is none or ancestor node is none break the loop
                if current.parent is None or current.parent.parent is None:
                    break
                # move to parent node
                current = current.parent
                # if can't find parent's brother continue
                if stream.find("<", current.close_tag_scope[1], current.parent.close_tag_scope[0]) == -1:
                    break
                # change parse scope
                parse_start, parse_end = current.close_tag_scope[1], current.parent.close_tag_scope[0]
                # create parent brother
                parent_brother_node = Node()
                # save ancestor address
                parent_brother_node.parent = current.parent
                # save parent's brother address
                current.parent.child.append(parent_brother_node)
                current = parent_brother_node
                continue
            else:
                # change parse scope
                parse_start, parse_end = traverse_end, current.parent.data_scope[1]
                # create brother node
                brother_node = Node()
                # save parent node address
                brother_node.parent = current.parent
                # save child node address
                current.parent.child.append(brother_node)
                # change current node
                current = brother_node
                continue
    except Exception as e:
        print("parse except : {0}".format(e))
    
    # change Tree to dict
    result = dict()