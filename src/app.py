import re
import glob
import pprint


def get_object_name(strobject):
    return strobject.split(' as ')[0].strip()


def get_modules(str_modules):
    return [get_object_name(s) for s in str_modules.split(',') if s]


def get_imports(source_lines):
    multiline_import = False
    ret = []
    for line in source_lines:
        grp = re.match(r"^\s*from (.[^,]+)\s+import\s+(\()\s*$", line)
        if grp:
            multiline_import = True
            fromstr = grp.groups()[0]
            continue
        if multiline_import:
            grp = re.match(r"^\s*(.*)\s*\)\s*$", line)
            if grp:
                multiline_import = False                
                importstr = grp.groups()[0]
            else:
                importstr = line
            lst_import = get_modules(importstr)
            for imp in lst_import:
                ret.append('{}.{}'.format(fromstr, imp))
        else:
            grp = re.match(r"^\s*import\s+([^\'\"]*)$", line)
            if grp:
                ret.extend(get_modules(grp.groups()[0]))
                continue
            grp = re.match(r"^\s*from (.[^,]+)\s+import\s+([^(]+)$", line)
            if grp:
                fromstr, importstr = grp.groups()
                lst_import = get_modules(importstr)
                for imp in lst_import:
                    ret.append('{}.{}'.format(fromstr, imp))
                continue
    return ret


def save_puml(base_tree, dct_file_imports):
    counter = {'i': 0}
    alias_map = {}

    def gen_alias(k):
        counter['i'] += 1
        return 'a{}'.format(counter['i'])

    def gen_tree_leaf(tree_leaf, tabs='', path=None):        
        for k, v in tree_leaf.items():
            alias = gen_alias(k)
            newpath = path + (k,) if path else (k,)
            alias_map[newpath] = alias
            if not v:     
                lines.append(f'{tabs}component "{k}" as {alias}')
            else:
                lines.append(f'{tabs}package {k} as {alias} {{')
                tabs_old = tabs
                tabs += '\t'
                gen_tree_leaf(v, tabs, newpath)
                tabs = tabs_old
                lines.append(f'{tabs}}}')

    def gen_connections(dct_file_imports):
        for filetuple, lst_imports in dct_file_imports.items():
            a_alias = alias_map.get(filetuple)
            if not a_alias:
                raise Exception('No alias found for {}'.format(filetuple))
            for imp in lst_imports:
                filetuple = tuple(imp.split('.'))
                b_alias = alias_map.get(filetuple)
                if not b_alias:
                    raise Exception('No alias found for {}'.format(filetuple))
                lines.append('{} --> {}'.format(a_alias, b_alias))

    lines = ['@startuml']
    gen_tree_leaf(base_tree)
    lines.append('\n\n')
    gen_connections(dct_file_imports)
    lines.append('@enduml')
    with open('diagram.puml', 'w') as f:
        f.write('\n'.join(lines))


def create_puml(dct_file_imports):
    base_tree = {}
    for file_tuple in dct_file_imports.keys():
        cur_tree = base_tree
        for n in file_tuple:
            cur_tree = cur_tree.setdefault(n, {})
    for lst_imports in dct_file_imports.values():        
        for imp in lst_imports:
            cur_tree = base_tree
            for n in imp.split('.'):
                cur_tree = cur_tree.setdefault(n, {})
    save_puml(base_tree, dct_file_imports)


def gen_py_files(root_path):
    for filename in glob.iglob(root_path + '**/*.py', recursive=True):
        if not filename.endswith('__init__.py'):
            if root_path + 'speedway_data_parser' in filename:
                yield filename


def filepath_to_std_path(filename, root_path):
    return tuple(filename.replace(root_path, '').replace('.py', '').split('/'))


def import_to_abs_import(imp, filetuple):
    if not imp.startswith('.'):
        return imp
    grp = re.match('^([.]+)(.+)$', imp)
    dots, rel_imp = grp.groups()
    comp = len(dots) - (len(filetuple) + 1)
    if comp > 0:
        raise ValueError('Incorrect relative import')
    elif comp == 0:
        return rel_imp
    else:
        endindex = len(dots) - 1
        if endindex == 0:
            return '.'.join(filetuple) + imp
        return '{}.{}'.format('.'.join(filetuple[:endindex]), rel_imp)
    

def main():
    root_path = './scan/speedway_data_parser/'
    dct_file_imports = {}
    for filename in gen_py_files(root_path):
        with open(filename, 'r') as f:            
            source_lines = f.read().splitlines()
        std_path = filepath_to_std_path(filename, root_path)
        lst_imports = get_imports(source_lines)
        dct_file_imports[std_path] = [import_to_abs_import(imp, std_path) for imp in lst_imports]
    create_puml(dct_file_imports)


if __name__ == '__main__':
    main()