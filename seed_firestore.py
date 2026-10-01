"""Seed script for K2P channels in Firestore.
Hardcodes project ID string: qwiklabs-gcp-04-02df96e1c54a.
"""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-04-02df96e1c54a"
COLLECTION_NAME = "k2p_channels"

SEEDED_ITEMS = [
    {
        "name": "TREK-1",
        "gene_symbol": "KCNK2",
        "subfamily": "TREK",
        "gating_triggers": [
            "Membrane stretch / mechanical force",
            "Intracellular acidosis (pH < 7.0)",
            "Polyunsaturated fatty acids (Arachidonic acid)",
            "Volatile general anesthetics (Halothane, Isoflurane)",
            "Warm temperature (>32°C)"
        ],
        "pharmacology": {
            "activators": ["Riluzole", "BL-1249", "ML335", "GI-530159"],
            "blockers": ["Spadin", "Fluoxetine", "Norfluoxetine", "Tetraethylammonium (TEA weak)"]
        },
        "summary": "TREK-1 is a thermosensitive and mechanosensitive two-pore domain background potassium channel. It is widely expressed in the central nervous system, heart, and smooth muscle, playing a pivotal role in general anesthesia, neuroprotection, and depression pathophysiology.",
        "key_references": [
            "Patel AJ, et al. A mammalian two pore domain mechano-gated S-like K+ channel. EMBO J. 1998.",
            "Lolicato M, et al. K2P2.1 (TREK-1) activator ML335 mechanism. Nature Chemical Biology, 2017.",
            "Heurteaux C, et al. Deletion of the TREK-1 potassium channel produces antidepressant-resistant behavior. PNAS, 2006."
        ]
    },
    {
        "name": "TRAAK",
        "gene_symbol": "KCNK4",
        "subfamily": "TREK",
        "gating_triggers": [
            "Membrane tension / mechanical stretch",
            "Lipid bilayer curvature and free arachidonic acid",
            "Alkaline intracellular pH (>7.5)"
        ],
        "pharmacology": {
            "activators": ["Arachidonic acid", "Riluzole"],
            "blockers": ["Ruthenium Red (weak)", "Spadin (weak)"]
        },
        "summary": "TRAAK (TWIK-Related Arachidonic acid-stimulated K+ channel) is mechanosensitive and lipid-regulated. It is predominantly localized to the mammalian nodes of Ranvier and sensory neurons, contributing to high-frequency action potential propagation and pain perception.",
        "key_references": [
            "Fink M, et al. Cloning, tissue distribution and functional expression of a mammalian two-pore domain K+ channel, TRAAK. EMBO J. 1998.",
            "Brohawn SG, et al. Crystal structure of the human K2P TRAAK, a lipid- and mechano-sensitive K+ channel. Science, 2012."
        ]
    },
    {
        "name": "TASK-3",
        "gene_symbol": "KCNK9",
        "subfamily": "TASK",
        "gating_triggers": [
            "Extracellular pH variations (inhibited by extracellular acidosis, pKa ~6.7)",
            "Inhibited by Gq-coupled receptor activation",
            "Activated by volatile anesthetics (Halothane)"
        ],
        "pharmacology": {
            "activators": ["Halothane", "Isoflurane"],
            "blockers": ["PK-THPP", "A1899", "Zinc ions (Zn2+)", "Bupivacaine"]
        },
        "summary": "TASK-3 is an acid-sensitive background potassium channel highly expressed in cerebellar granule neurons, locus coeruleus, and motoneurons. It regulates resting membrane potential, sleep architecture, and respiratory chemoreception, and is often overexpressed in carcinomas.",
        "key_references": [
            "Kim D, et al. Cloning and functional expression of a human acid-sensitive K+ channel TASK-3. J Biol Chem. 2000.",
            "Linden AM, et al. TASK-3 knockout mice exhibit altered sensitivity to inhalation anesthetics. J Pharmacol Exp Ther. 2007."
        ]
    },
    {
        "name": "TRESK",
        "gene_symbol": "KCNK18",
        "subfamily": "TRESK",
        "gating_triggers": [
            "Intracellular calcium elevation via calcineurin phosphatase activation",
            "Phosphorylation by 14-3-3 adaptor proteins (inactivation)"
        ],
        "pharmacology": {
            "activators": ["Cloxyquin", "Calcineurin agonists"],
            "blockers": ["Lamotrigine", "Amiloride", "Isobutylmethylxanthine (IBMX)"]
        },
        "summary": "TRESK is the only K2P channel directly gated by intracellular calcium-calcineurin signaling. Abundantly expressed in primary sensory dorsal root ganglia (DRG) and trigeminal ganglia, its mutations are strongly implicated in familial migraine with aura.",
        "key_references": [
            "Sano Y, et al. A novel two-pore domain K+ channel, TRESK, is activated by the calcium-dependent phosphatase calcineurin. J Biol Chem. 2003.",
            "Lafrenière RG, et al. A dominant-negative mutation in the TRESK potassium channel causes familial typical migraine with aura. Nat Med. 2010."
        ]
    }
]


def seed():
    print(f"Connecting to Firestore for project: {PROJECT_ID}...")
    db = firestore.Client(project=PROJECT_ID)
    batch = db.batch()
    for item in SEEDED_ITEMS:
        doc_ref = db.collection(COLLECTION_NAME).document(item["name"])
        batch.set(doc_ref, item)
        print(f"  Queued: {item['name']} ({item['gene_symbol']})")
    batch.commit()
    print(f"Successfully seeded {len(SEEDED_ITEMS)} K2P channel documents into '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    seed()
