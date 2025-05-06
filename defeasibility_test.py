from tree import TreeNode
from text_processing import text_label

from solver import make_tree
from solver import make_tree_inference, get_leaves, make_tree_inference_defe



TreeNode.reset_tree()

text = "Everyone is happy"
conclusion = ""

root, boolean = make_tree_inference(text, conclusion)

print("Are all contradictions?")
print (boolean)

new_statement = "Bob is not happy"

leaf_nodes = get_leaves(root)
open_nodes = [node for node in leaf_nodes if not node.value.get("Contradiction", False).any()]

final_boolean = True
for node in open_nodes:
    df = node.value
    current_true = df.at[0, "True Statements"]
    if isinstance(current_true, list):
        current_true.append(new_statement)
    elif current_true == "":
        current_true = [new_statement]
    else:
        current_true = [current_true, new_statement]
    
    subtree_root, subtree_boolean = make_tree_inference_defe(current_true, df.at[0, "False Statements"], new_statement)
    if not subtree_boolean:
        final_boolean = True
    node.children = [subtree_root]

root.display_tree()

print("Are all contradictions?")
print (final_boolean)