import streamlit as st
from solver import make_tree_inference, get_leaves, make_tree_inference_defe
from tree import TreeNode
import pandas as pd

rule_explanations = {
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
    14: "Negation of a false statement -> The statement is true, place it in the true statements."
}

examples = {
    "Custom": ("", ""),
    "Example 1 - Simple Negation": ("I am not sad", ""),
    "Example 2 - Modus Tollens": ("If it is raining then the ground is wet. The ground is not wet.", "It is not raining."),
    "Example 3 - Modus Ponens": ("If Alice sings then Bob smiles. Alice sings.", "Bob smiles."),
    "Example 4 - Hypothetical Syllogism": ("If I eat then I am full. If I am full then I sleep. I eat.", "I sleep."),
    "Example 5 - Disjunctive Syllogism": ("Either the lamp is on or the window is open. The lamp is not on.", "The window is open."),
    "Example 6 - Conjunction Simplification": ("The cat is golden and the cat is happy.", "The cat is golden."),
    "Example 7 - Negation of a Conjunction": ("It is not the case that the door is open and the window is shut.", ""),
    "Example 8 - Universal Quantifier": ("All singers are happy. Alice is a singer.", "Alice is happy."),
    "Example 9 - Existential Quantifier": ("Some students are smart.", ""),
    "Example 10 - Negated Universal (¬∀ → ∃¬)": ("It is not the case that all teachers are kind.", ""),
    "Example 11 - Biconditional": ("The moon is full if and only if the sky is clear. The moon is full.", "The sky is clear."),
    "Example 12 - Contradiction Check": ("All dogs are animals. No animals are pets. All dogs are pets.", ""),
    "Example 13 - Double Negation": ("It is not the case that it is not raining.", "It is raining."),

}

st.set_page_config(page_title="Semantic Tableau Solver", layout="wide")
st.title("Semantic Tableau Visualizer")

st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("**What is the Semantic Tableau Method? (Click to expand for more information)**"):
    st.markdown("""
                

                
The **Semantic Tableau** is a method used in logic to determine whether a conclusion logically follows from a set of premises.

---

### The intuition:
Here is an example. You have the following premises: "If I am sad, then I cry", and "I am sad". These are sentences you know to be true. 
You then have a conclusion: "I cry". 
                
Your goal is to determine whether this conclusion logically follows the premises, meaning that this conclusion is always true, given the premises. How can you prove this?
                
The tableau solver works by assuming that the premises are true, and the conclusion is false. 
                
It will then try to find contradictions within this assumption. If we discover that assuming the conclusion is false always leads to a contradiction, then we know that the conclusion must be true!
                
Therefore, if you find only contradictions, you know that your original inference (premises + conclusion) is **logically valid**

But how does the solver find these contradictions?
                
The tableau solver builds a logic tree, starting with the initial premises and conclusion, and applying rules to these statements to solve them until we find contradictions (or until they can no longer be solved).
Each node of the tree will contain statements that we know to be true and statements we know to be false. 

---

### How it Starts:
- All **premises** are placed on the **true** side.
- The **conclusion** is placed on the **false** side.
- Then, the system starts breaking down complex statements using **logical rules** until:
  - We hit a **contradiction** (branch closes), or
  - We reach a point where no more rules apply and **no contradiction appears** (branch remains open).

---

### Why It Works:
- The method is based on the principle of **reductio ad absurdum** — assuming the opposite of what you want to prove and showing it leads to an inconsistency.
- If **all branches** close (contradiction in every case), it means there's **no way** the conclusion could be false if the premises are true — the argument is **logically valid**.
- If **any branch** remains open, then there’s at least one logical scenario where the conclusion doesn’t follow — the argument is **not universally valid**.

---

### How It Solves:
The solver uses a set of logic rules to simplify or split statements. Here are a few examples:

- **¬(A or B)** → both ¬A and ¬B must be true. Example: "It is not the case that I am sad or I am tired" is the same as saying "I am not sad and I am not tired".
- **If A then B** (A → B) is true → either ¬A is true, or B is true. Example: "If it rains then the ground is wet" is the same as saying "Either it is not raining, or the ground is wet".

Sometimes, while applying these rules, the tree generates 2 branches. This happens because you have reached a point where there are two different possible explanations for what could be true — but you're not sure which one it is yet. 
                
Instead of picking one, you explore both options separately, like a fork in the road. 

For example:

If we know that "Either Alice is dancing or Bob is singing", but we don’t know which one is true — it could be Alice, Bob, or both — so we branch into:

- One path where we assume Alice is dancing is true.
- Another path where we assume Bob is singing is true.
  
The tree keeps solving each of these branches separately. If both lead to a contradiction, we know the original assumption doesn't work. But if one of them still works, the whole argument might still be logically possible.
                

""")
    
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
            

### Welcome to the Semantic Tableau Visualizer

Enter a logical sentence and an optional conclusion. The app will automatically build a **semantic tableau** (logic tree) that breaks down the reasoning process step by step, applying formal logic rules to determine whether the conclusion follows.

---

####  How to Use:
- Choose an example from the dropdown, or select "Custom" and type your own sentence and conclusion.
- You can leave the checkbox **"Show full DataFrame for each node"** unchecked, unless you want more details on what is going on behind the scenes
- Click **"Run Semantic Tableau Solver"** to generate the logic tree.
- Whenever you have an inteded line that means the node is a child of the previous indentation level, you can also see this by the depth level specified
- Expand each node to see how rules were applied and which statements are considered true or false at each step.

---

####  What the Node Colors Mean:
- 🔴 **Red Node**: A **contradiction** was found — this branch **closes**.
- 🟡 **Yellow Node**: The branch **remains open** (no contradiction found and no more rules can be applied).
- ⚪ **White Node**: An **intermediate node**, still in progress.

---

####  Final Evaluation:
- If all ending branches are **red (closed)**, so there are **no yellow nodes**:
  - This means **every possible interpretation** of the statements leads to a contradiction.
  - Therefore, the **negation of the conclusion is impossible**, which implies that the original argument is **logically valid** — the conclusion must follow from the premises.
- If there are any **yellow nodes**, meaning some branches remain open:
  - At least one **counterexample** exists where the premises are true and the conclusion does not follow.
  - Thus, the argument is **not universally valid**.

            

""")

st.markdown("<br><br>", unsafe_allow_html=True)

with st.expander("**What kind of sentences can I write in 'Custom'? (Click for details)**"):
    st.markdown("""
                

This solver understands **simple, well-formed English sentences** — but keep in mind, it doesn't have common sense or real-world knowledge. It only knows the logic you give it.

---

### General Guidelines:
- Keep sentences **short** and **simple**.
- Use **proper grammar** and avoid typos — otherwise, the system may get confused.
- Use **full stops** to separate multiple sentences.
- Proper names (like Alice, Bob, etc.) should start with a **capital letter**.
- Sentences should describe facts or rules, not questions or commands.
- Avoid idioms or abstract language — be literal and clear.

---

### Sentence types you can use:

#### ✅ **Basic Statements**:
- `The cat jumps.`
- `Alice sings.`
- `I am happy.`

#### ✅ **Negations**:
- `The dog doesn't bark.`
- `Nobody smiles.`
- `No student jumps.`

#### ✅ **Conjunctions (AND)**:
- `The lamp is golden and the lamp is heavy.`
- `Luisa and Socrates are happy.`

#### ✅ **Disjunctions (OR)**:
- `Either Alice sings or Bob dances.`
- `I eat or I drink.`
- `Mary doesn't eat fish or meat.`

#### ✅ **Conditionals (IF...THEN)**:
- `If the cat sings, then Bob smiles.`
- `If nobody sings, then Alice cries.`

#### ✅ **Biconditionals (IF AND ONLY IF)**:
- `Alice dances if and only if Bob sings.`

#### ✅ **Causal-like language** *(mapped to logic)*:
- `Bob jumps because the bell rings.`

#### ✅ **Quantifiers**:
- `All students read.`
- `Some people run.`
- `Nobody eats.`
- `I don't love anyone.`
- `Everyone hates everyone.`
- `All who (verb + object) (verb + object)` -> example: All who play tennis are happy
- `If one (verb + object), then one (verb + object)` -> use this structure for a rule that applies to everyone, example: If one plays tennis, then one is happy

---

### Special Notes:
- The system **does not understand real-world context** — so you can say things like:
  - `"If the cat teaches the piano, then every student jumps the newspaper."` and it will still try to process it logically.
- **Spelling and grammar matter.** The sentence:
  - ✅ `The cat jumps.`
  - ❌ `The cat jump.` ← (incorrect verb conjugation)

- Proper nouns must be **capitalized** (`Alice`, `Bob`, `Mary`).
- **Compound names** like `The tall man` or `The happy student` are fine.
- **Unrecognized names** may cause errors — stick with simple names or those used in examples.

         

""")


st.markdown("<br><br>", unsafe_allow_html=True)

if "tree_root" not in st.session_state:
    st.session_state.tree_root = None
if "contradiction_status" not in st.session_state:
    st.session_state.contradiction_status = None

col1, col2 = st.columns(2)
with col1:
    selected_example = st.selectbox("Choose an example:", list(examples.keys()))
with col2:
    if selected_example != "Custom":
        input_text, conclusion = examples[selected_example]
    else:
        input_text = st.text_input("Enter your sentence:", key="custom_input")
        conclusion = st.text_input("Enter your conclusion (optional):", key="custom_conclusion")

show_full_df = st.checkbox("Show full DataFrame for each node", value=False)

if selected_example != "Custom":
    st.text_input("Input Sentence:", value=input_text, key="locked_input", disabled=True)
    st.text_input("Conclusion (optional):", value=conclusion, key="locked_conclusion", disabled=True)

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

    # if node.node_id == 0:
    #     for child in node.children:
    #         display_node(child, depth + 1)
    #     return

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
                elif pd.isna(highlight):
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




if st.button("Run Semantic Tableau Solver"):
    
    with st.spinner("Processing..."):
        try:
            TreeNode.reset_tree()
            root, all_contradictions = make_tree_inference(input_text, conclusion)
            st.session_state.tree_root = root
            st.session_state.contradiction_status = all_contradictions
            st.success("Tree generated. All branches closed: {}".format("Yes" if all_contradictions else "No"))

        
            display_node(root)

            st.markdown("---")
            if all_contradictions:
                st.success("All branches have been closed. This means the initial statement logically leads to a contradiction in every case — the inference is **logically valid**.")
            else:
                st.warning("Some branches remain open. This means there is at least one interpretation where the statements hold without contradiction — the inference is **not necessarily valid**.")
        except Exception as e:
            st.error(" Oops! Something went wrong while processing your sentence. Please check your input for typos or unsupported sentence structures.")





st.markdown("---")
st.markdown("### Add a New Statement (Defeasibility Check)")

if st.session_state.tree_root:
    with st.form("defeasibility_form"):
        new_statement = st.text_input("Enter an additional statement to test defeasibility:")
        submitted = st.form_submit_button("Apply Statement to Open Branches")

    if submitted and new_statement:
        try:
            st.info(f"New statement added: '{new_statement}'")
            leaf_nodes = get_leaves(st.session_state.tree_root)
            open_nodes = [node for node in leaf_nodes if not node.value.get("Contradiction", pd.Series(False)).any()]


            for node in open_nodes:
                df = node.value
            # display_node(node)


                current_true = df.at[0, "True Statements"]
                if isinstance(current_true, list):
                    current_true.append(new_statement)
                elif current_true == "":
                    current_true = [new_statement]
                else:
                    current_true = [current_true, new_statement]
                
                subtree_root, _ = make_tree_inference_defe(current_true, df.at[0, "False Statements"], new_statement)
                node.children = [subtree_root]

            st.success("Defeasibility applied. Updated open branches with the new statement.")
            display_node(st.session_state.tree_root)
        except Exception as e:
            st.error(" Oops! Something went wrong while processing your sentence. Please check your input for typos or unsupported sentence structures.")
else:
    st.info("Run the solver above first before using defeasibility.")
