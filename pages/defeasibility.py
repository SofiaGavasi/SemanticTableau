import streamlit as st
import streamlit as st
from solver import make_tree_inference, get_leaves, make_tree_inference_defe
from tree import TreeNode
import pandas as pd
from text_processing import text_label
from collections import defaultdict
from itertools import product
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

rule_explanations = {
    -1: "Initialization: Just placing the sentence into the node.",
    0: "Initialization: Just placing the sentence into the node.",
    1: "AND on the left (positive): Break 'A and B' into A and B.",
    2: "AND on the right (negative): Create two branches, one with ¬A and one with ¬B.",
    3: "OR on the left (positive): Create two branches, one with A and one with B.",
    4: "OR on the right (negative): Break '¬(A or B)' into ¬A and ¬B.",
    5: "Implication (→) on the left (positive): Break 'A → B' into ¬A or B (branch).",
    6: "Implication (→) on the right (negative): Break '¬(A → B)' into A and ¬B.",
    7: "Biconditional (↔) on the left: Break into A → B and B → A.",
    8: "Biconditional (↔) on the right: Branch into 'A and ¬B' and '¬A and B'.",
    9: "Universal quantifier on the left: Apply ∀x.P(x) to each relevant instance.",
    10: "Universal quantifier on the right: Use counterexample ¬P(a).",
    11: "Existential quantifier on the left: Use a new instance P(a).",
    12: "Existential quantifier on the right: Must hold for all, show ¬P(x).",
    13: "Negation of a true statement -> The statement is false, place it in the false statements.",
    14: "Negation of a false statement -> The statement is true, place it in the true statements.",
    16: "Expansion of a universal statement"
}


if "tree_root" not in st.session_state:
    st.session_state.tree_root = None
if "contradiction_status" not in st.session_state:
    st.session_state.contradiction_status = None

if "premises" not in st.session_state:
    st.session_state.premises = ["", ""]





def color_sentence(sentence, highlight_list, true_contradictions, false_contradictions, is_true, defeasible=None):
    if defeasible and sentence == defeasible:
        return f"<span style='color: blue; font-weight: bold'>{sentence}</span>"
    if is_true and sentence in true_contradictions:
        return f"<span style='color: red; font-weight: bold'>{sentence}</span>"
    elif not is_true and sentence in false_contradictions:
        return f"<span style='color: red; font-weight: bold'>{sentence}</span>"
    elif sentence in highlight_list:
        return f"<span style='color: green; font-weight: bold'>{sentence}</span>"
    else:
        return sentence


def format_list_column(col, highlight_list, true_contradictions, false_contradictions, is_true):
    if isinstance(col, list):
        return ", ".join([color_sentence(s.strip(), highlight_list, true_contradictions, false_contradictions, is_true) for s in col])
    else:
        return color_sentence(col.strip(), highlight_list, true_contradictions, false_contradictions, is_true)


def highlight_dataframe(df, highlight_list, true_contradictions, false_contradictions):
    df_copy = df.copy()
    if "True Statements" in df_copy.columns:
        df_copy["True Statements"] = df_copy["True Statements"].apply(
            lambda x: format_list_column(x, highlight_list, true_contradictions, false_contradictions, is_true=True)
        )
    if "False Statements" in df_copy.columns:
        df_copy["False Statements"] = df_copy["False Statements"].apply(
            lambda x: format_list_column(x, highlight_list, true_contradictions, false_contradictions, is_true=False)
        )
    return df_copy.to_html(escape=False, index=False)



def display_node(node, depth=0, parent=None):

    if node.node_id == 0 and any(
        0 in child.value.copy().get("Rule", pd.Series(dtype=int)).dropna().tolist()
        for child in node.children
    ):

        for child in node.children:
             display_node(child, depth + 1)
        return

    indent = "\u2007" * (depth * 4)
    node_prefix = "⚪"
    label_clean = f"Node {node.node_id} (Depth {depth})"

    contradiction_found = False
    branch_open = False

    if isinstance(node.value, pd.DataFrame) and not node.value.empty:
        df = node.value.copy()
        defeasible_statement = df["Defeasible"].iloc[0] if "Defeasible" in df.columns else None
        if defeasible_statement:
            st.info(f'The statement "{defeasible_statement}" was added in the True Statements.')
        contradiction_found = df.get("Contradiction", pd.Series(False)).any()
        branch_open = df.get("End", pd.Series(False)).any() and not contradiction_found and not node.children

        if contradiction_found:
            node_prefix = "🔴"
        elif branch_open:
            node_prefix = "🟡"

        with st.expander(f"{indent}{node_prefix} {label_clean}", expanded=False):
            highlight_list = df['Highlight'].dropna().tolist()
            highlight_list = [item for sublist in highlight_list for item in (sublist if isinstance(sublist, list) else [sublist])]

            true_contradictions = df.get("True Contradiction", pd.Series(dtype=str)).dropna().tolist()
            false_contradictions = df.get("False Contradiction", pd.Series(dtype=str)).dropna().tolist()


            st.write("### Raw Statements")
            if show_full_df:
                st.markdown(highlight_dataframe(df, highlight_list, true_contradictions, false_contradictions), unsafe_allow_html=True)

            else:
                subset_df = df[[col for col in ["True Statements", "False Statements"] if col in df.columns]]
                st.markdown(highlight_dataframe(subset_df, highlight_list, true_contradictions, false_contradictions), unsafe_allow_html=True)

            for idx, row in df.iterrows():
                rule_id = row.get("Rule")
                rule_label = rule_explanations.get(rule_id, "Unknown rule")
                parent_sentence = row.get("Parent", "")
                highlight = row.get("Highlight", [])

                if isinstance(highlight, str):
                    highlight = [highlight]
                elif pd.isna(highlight).any():
                    highlight = []


                branching_rules = [2, 3, 5, 8]
                sibling_highlights = []
                if rule_id in branching_rules and parent:
                    for sibling in parent.children:
                        if sibling is not node and isinstance(sibling.value, pd.DataFrame):
                            highlights = sibling.value["Highlight"].dropna().tolist()
                            for h in highlights:
                                if isinstance(h, list):
                                    sibling_highlights.extend(h)
                                else:
                                    sibling_highlights.append(h)


                if pd.notna(parent_sentence):
                    if rule_id in branching_rules and sibling_highlights:
                        explanation = f"""
                **Rule {rule_id}** applied from _"{parent_sentence}"_: {rule_label}  
                This rule splits the sentence into two branches:
                - This branch contains: {", ".join(f'"{h}"' for h in highlight)}
                - The other branch contains: {", ".join(f'"{s}"' for s in sibling_highlights)}
                """
                    else:
                        explanation = f"""
                **Rule {rule_id}** applied from _"{parent_sentence}"_: {rule_label}  
                So from _"{parent_sentence}"_, we add: {", ".join(f'"{h}"' for h in highlight)}
                """
                else:
                    explanation = f"**Rule {rule_id}**: {rule_label}"

                st.markdown(explanation)




                true_contradiction = row.get("True Contradiction")
                false_contradiction = row.get("False Contradiction")
                if pd.notna(true_contradiction) and pd.notna(false_contradiction):
                    st.error(f"A contradiction was found because \"{true_contradiction}\" is said to be true and \"{false_contradiction}\" is said to be false.")

            def render_statement_list(title, items, is_true, highlight_list, true_contradictions, false_contradictions, defeasible=None):
                if items:
                    st.markdown(f"### {title}")
                    for stmt in items:
                        colorized = color_sentence(stmt, highlight_list, true_contradictions, false_contradictions, is_true, defeasible)
                        st.markdown(f"- {colorized}", unsafe_allow_html=True)


            true_statements = []
            for s in df['True Statements'].dropna():
                if isinstance(s, list):
                    true_statements.extend(s)
                else:
                    true_statements.append(s)

            false_statements = []
            for s in df['False Statements'].dropna():
                if isinstance(s, list):
                    false_statements.extend(s)
                else:
                    false_statements.append(s)

            render_statement_list("Sentences we know are true:", true_statements, is_true=True, highlight_list=highlight_list, true_contradictions=true_contradictions, false_contradictions=false_contradictions, defeasible=defeasible_statement)
            render_statement_list("Sentences we know are false:", false_statements, is_true=False, highlight_list=highlight_list, true_contradictions=true_contradictions, false_contradictions=false_contradictions, defeasible=defeasible_statement)



            if node.children:
                children_ids = [str(child.node_id) for child in node.children]
                num = len(children_ids)
                label = "child" if num == 1 else "children"
                parent_sentence = node.children[0].value.get("Parent", [None])[0] if "Parent" in node.children[0].value.columns else None
                if parent_sentence:
                    st.info(f"From here, we solve the sentence \"{parent_sentence}\", and we will have {num} {label}, which are node(s): {', '.join(children_ids)}")
                else:
                    st.info(f"From here we have {num} {label}, which are node(s): {', '.join(children_ids)}")
            elif branch_open:
                st.warning(f"The sentences can be solved no further and there are no contradictions, so the branch is open")

    for child in node.children:
        display_node(child, depth + 1, parent=node)





def build_full_sentence(premises):
    cleaned = [p.strip().rstrip('.') + '.' for p in premises if p.strip()]
    return ' '.join(cleaned)


col1, col2 = st.columns(2)

i = 0
while i < len(st.session_state.premises):
    st.session_state.premises[i] = st.text_input(f"Premise {i+1}", st.session_state.premises[i], key=f"premise_{i}")
    i += 1
if st.button("➕ Add another premise"):
    st.session_state.premises.append("")
conclusion = st.text_input("Conclusion (optional):", key="conclusion_input")
input_text = build_full_sentence(st.session_state.premises)
show_full_df = st.checkbox("Show full DataFrame for each node", value=False)
if st.button("Run Semantic Tableau Solver"):
    with st.spinner("Processing..."):
        TreeNode.reset_tree()
        root, all_contradictions = make_tree_inference(input_text, conclusion)
        st.session_state.tree_root = root
        st.session_state.contradiction_status = all_contradictions
        st.success("Initial tree generated. All branches closed: {}".format("Yes" if all_contradictions else "No"))
        st.markdown("---")
        if all_contradictions:
            st.success("All branches have been closed. This means the initial statement logically leads to a contradiction in every case — the inference is **logically valid**.")
        else:
            st.warning("Some branches remain open. This means there is at least one interpretation where the statements hold without contradiction — the inference is **not necessarily valid**.")
            st.write("Now possible rules will be tried and evaluated.")
            statements = {
                "Subject": [],
                "Verb": [],
                "Object": []
            }

            premises = input_text
            sentences = [s.strip() for s in premises.split('.') if s.strip()]
            print(sentences)

            for sent in sentences:
                sentence_df = text_label(sent)
                or_sentence = sentence_df.loc[0, "Full sentence"]
                sentence_split = or_sentence.split()
                subject = sentence_split[int(sentence_df.loc[0, "Subject"])]
                verb = sentence_split[int(sentence_df.loc[0, "Verb"])]
                obj_index = sentence_df.loc[0, "Obj"]
                obj = None
                if obj_index:
                    obj = sentence_split[int(obj_index)]
                statements["Subject"].append(subject)
                statements["Verb"].append(verb)
                statements["Object"].append(obj)
            print(statements)


            subject_indices = defaultdict(list)
            for idx, subject in enumerate(statements['Subject']):
                subject_indices[subject].append(idx)

            print(subject_indices)

            new_sentences = []
            for subject, indices in subject_indices.items():
                if len(indices) > 1:
                    for i, j in product(indices, repeat=2):
                        if i != j: 
                            verb1, obj1 = statements['Verb'][i], statements['Object'][i]
                            verb2, obj2 = statements['Verb'][j], statements['Object'][j]
                            if obj1 is None and obj2 is None:
                                sentence = f"If one {verb1} then one {verb2}."
                            elif obj1 is None:
                                sentence = f"If one {verb1} then one {verb2} {obj2}."
                            elif obj2 is None:
                                sentence = f"If one {verb1} {obj1} then one {verb2}."
                            else:
                                sentence = f"If one {verb1} {obj1} then one {verb2} {obj2}."
                            new_sentences.append(sentence)


            valid_statements = []
            probable_statements = []
            for s in new_sentences:
                test_premises = premises + " " + s
                TreeNode.reset_tree()
                root, boolean = make_tree_inference(test_premises, "")
                if not boolean: 
                    valid_statements.append(s)
                    TreeNode.reset_tree()
                    root, boolean = make_tree_inference(test_premises, conclusion)
                    if boolean:
                        probable_statements.append(s)
                        good_root = root
                        
            if probable_statements:
                st.markdown(" #### The rules that seem possible given the initial premises and conclusion are:")
                for s in probable_statements:
                    st.markdown(f"- {s}")
                st.markdown(" ##### As an example, the tree generated by the last one is:")
                display_node(good_root)
                st.success("All branches have been closed. This means the initial statement logically leads to a contradiction in every case — the inference is **logically valid**.")
            else:
                st.error("No rules that satisfy the conclusion could be found")


