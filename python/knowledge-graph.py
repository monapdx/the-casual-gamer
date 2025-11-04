
import spacy
import networkx as nx
import matplotlib.pyplot as plt

def extract_entities_and_relationships(text):
    # Load spaCy language model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    entities = []
    relationships = []

    # Extract named entities
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    # Extract relationships
    for token in doc:
        if token.dep_ == "ROOT" and token.head == token:  # Main action
            subject = [child for child in token.children if child.dep_ in ["nsubj", "nsubjpass"]]
            object_ = [child for child in token.children if child.dep_ in ["dobj", "pobj"]]

            if subject and object_:
                relationships.append((subject[0].text, token.text, object_[0].text))

    return entities, relationships

def create_knowledge_graph(entities, relationships):
    G = nx.DiGraph()

    # Add entity nodes
    for entity, label in entities:
        G.add_node(entity, label=label)

    # Add relationship edges
    for subj, action, obj in relationships:
        G.add_edge(subj, obj, label=action)

    return G

def visualize_graph(G):
    pos = nx.spring_layout(G)  # Layout for visualization
    plt.figure(figsize=(12, 8))

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=900, node_color="lightblue")

    # Draw edges
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=20)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    plt.title("Knowledge Graph")
    plt.show()

if __name__ == "__main__":
    # File path to your text document
    file_path = "C:\\Users\\Ash\\Downloads\\The Ins & Outs of Escorting.txt"  # Replace with your file path

    try:
        # Read text from the file
        with open(file_path, "r", encoding="utf-8") as file:
            text = file.read()

        entities, relationships = extract_entities_and_relationships(text)
        print("Entities:", entities)
        print("Relationships:", relationships)

        G = create_knowledge_graph(entities, relationships)
        visualize_graph(G)

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
