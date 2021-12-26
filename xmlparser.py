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

        self.is_traversed = False # boolean, using to change tree to dictionary
    
    def __str__(self):
        p = self.parent.name if not self.parent is None else "-"
        n = self.name
        return "name : {0}, parent : {1}".format(n,p)
    
    def summary(self):
        n = self.name
        p = "-" if self.parent is None else self.parent.name
        c = "-" if self.child is None else [children.name for children in self.child]
        d = "-" if self.data is None else self.data
        a = "-" if self.attribute is None else self.attribute
        return "name : {0}, parent : {1}, child : {2}, attribute : {3}, data : {4}".format(n,p,c,a,d)

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
            tag_end = tag_end1 + 1 if tag_end1 < tag_end2 else tag_end2 + 2
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
            attribute_data["@" + k] = v
        if attribute_data: # dictionaory is not empty
            self.attribute = attribute_data
        return True
    
    def parse_close_tag(self, stream, end):
        if self.is_contain:
            self.close_tag_scope = (self.open_tag_scope[1], self.open_tag_scope[1])
            return True
        tag_start = stream.find("</{0}>".format(self.name), self.open_tag_scope[1], end)
        if tag_start == -1:
            return None
        self.close_tag_scope = (tag_start, tag_start + len("</{0}>".format(self.name)))
        return True
    
    def parse_data(self, stream):
        if self.is_contain:
            self.data_scope = (self.open_tag_scope[1], self.open_tag_scope[1])
            return (self.open_tag_scope[1], self.open_tag_scope[1])
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
            #print(current)
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

    # tree traverse
    current = root
    result = dict()
    stack = [result]
    while True:
        # mark node
        current.is_traversed = True
        # 겹치는 이름이 존재하는 경우
        if current.name in stack[-1].keys():
            # 데이터를 리스트로 변환한 경우
            if type(stack[-1][current.name]) == list:
                # 데이터만 있는 경우라면
                if not current.data is None:
                    stack[-1][current.name].append(current.data)
                # 속성, 속성값만 있는 경우라면
                elif not current.attribute is None:
                    temp = dict()
                    for k, v in current.attribute.items():
                        temp[k] = v
                    stack[-1][current.name].append(temp)
                    stack.append(temp)
                # 데이터도 속성도 없는 경우
                else:
                    stack[-1][current.name].append(dict())
                    stack.append(temp)
            # 데이터가 아직 리스트로 변환되지 않은 경우
            else:
                # 리스트에 기존 딕셔너리를 담고
                temp = [stack[-1][current.name]]
                # 딕셔너리에서 리스트로 변경
                stack[-1][current.name] = temp
                # 데이터만 있다면
                if not current.data is None:
                    stack[-1][current.name].append(current.data)
                # 속성, 속성값이 존재한다면
                elif not current.attribute is None:
                    node_data = dict()
                    for k, v in current.attribute.items():
                        node_data[k] = v
                    stack[-1][current.name].append(node_data)
                    stack.append(node_data)
                else:
                    node_data = dict()
                    stack[-1][current.name].append(node_data)
                    stack.append(node_data)
            # 데이터를 리스트로 변환하지 않은 경우
        # 겹치는 이름이 존재하지 않을 경우
        else:
            # 데이터가 있는 경우라면
            if not current.data is None:
                # top에다가 데이터가 있는 노드를 갱신
                stack[-1][current.name] = current.data
            # 속성, 속성값만 있을 때
            elif not current.attribute is None:
                # 대응하는 사전 생성
                stack[-1][current.name] = dict()
                # 사전에 속성, 속성값 데이터 추가
                for k, v in current.attribute.items():
                    stack[-1][current.name][k] = v
                # 스택의 top에다가 사전 추가
                stack.append(stack[-1][current.name])
            # 데이터도 속성도 없는 경우
            else:
                # 대응하는 사전 생성
                stack[-1][current.name] = dict()
                # 스택에 top에다가 사전 추가
                stack.append(stack[-1][current.name])
        # print node summary
        #print(current.summary())
        # check child
        if not current.child is None: 
            child_flag = False
            for children in current.child:
                if not children.is_traversed:
                    current = children
                    child_flag = True
                    break
            if child_flag:
                continue
        # check brother
        brother_flag = False
        while not current.parent is None:
            if not current.parent.child is None:
                for brother in current.parent.child:
                    if not brother.is_traversed:              
                        current = brother
                        brother_flag = True
                        break
            if brother_flag:
                break
            else:
                current = current.parent
                stack.pop()
        if not brother_flag:
            break
    
    print(result)
