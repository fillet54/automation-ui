import os, subprocess
import json
import config

def find_git_root(path):
    return subprocess.Popen(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE).communicate()[0].rstrip()

def get_worktrees(git_path):
    def name_and_branch(worktree):
        parts = worktree.rsplit(' ', 2)
        return parts[0], parts[2].strip('[]')

    cmd = ['git', '-C', git_path, 'worktree', 'list']
    return [name_and_branch(worktree)
            for worktree in subprocess.check_output(cmd).decode('utf-8').splitlines()]

def get_treedata(root, virtual_root, unix_style=True, is_root=False):
    def path_join(*args):
        if unix_style:
            return "/".join(args)
        else:
            return os.path.join(args)

    treedata = [{
       'path': virtual_root,
       'type': 'folder',
       'children': []
    }]

    if is_root:
        treedata[-1]['isRoot'] = True

    try:
        root, dirs, files = next(os.walk(root))
    except StopIteration:
        return treedata
    
    # add children to folder
    treedata[-1]['children'] = [name for name in files+dirs]

    for name in files:
         treedata.append({
             'path': path_join(virtual_root, name),
             'type': 'file'
         })

    # add folders
    for dirname in dirs:
        treedata += get_treedata(os.path.join(root, dirname), path_join(virtual_root, dirname), unix_style=unix_style)
 
    return treedata
  
def rvt_tree_handler(request):
    print(config.rvt_paths)

    data = []
    for root in config.rvt_paths:
        data += get_treedata(root, 'rvt', is_root=True)
    tree_data = {node['path']:node for node in data}

    return {
        'status': 200,
        'headers': [('Content-Type', 'application/json')],
        'body': tree_data  
    }