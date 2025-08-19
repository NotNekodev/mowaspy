# /// script
# dependencies = [
#   "sentence-transformers",
#   "scikit-learn"
# ]
# ///


import time
from sentence_transformers import SentenceTransformer, util
from sklearn.linear_model import LogisticRegression
import pickle
import re

# -----------------------------
# 1. Load models
# -----------------------------
start_total = time.time()

start = time.time()
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
end = time.time()
print(f"Model load time: {(end - start)*1000:.1f} ms")

# Load or train classifier
start = time.time()
try:
    with open("classifier.pkl", "rb") as f:
        classifier = pickle.load(f)
except FileNotFoundError:
    train_texts = [
        "Heavy rain caused flash floods in the city.",
        "Police arrested a suspect in downtown robbery.",
        "New political reforms announced by government.",
        "Vilniaus policija surengė reidą narkotikų prekybos tinklui.",
        "Muitinė sulaikė 200 kg musmirių kontrabandos siuntą.",
        "Paprastoji musmirė turi psichoaktyvių medžiagų, kurios gali apsinuodyti."
    ]
    train_labels = ["Disaster", "Police", "Politics", "Police", "Drugs", "Drugs"]
    X = embedding_model.encode(train_texts, convert_to_numpy=True, normalize_embeddings=True)
    classifier = LogisticRegression(max_iter=1000)
    classifier.fit(X, train_labels)
    with open("classifier.pkl", "wb") as f:
        pickle.dump(classifier, f)
end = time.time()
print(f"Classifier load/train time: {(end - start)*1000:.1f} ms")

# -----------------------------
# 2. Helper functions
# -----------------------------
def split_sentences(text):
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if s]

def summarize(text, top_k=3):
    start = time.time()
    sentences = split_sentences(text)
    if not sentences:
        return "", 0

    start_embed = time.time()
    embeddings = embedding_model.encode(sentences, convert_to_numpy=True, normalize_embeddings=True)
    doc_embedding = embedding_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    end_embed = time.time()

    start_sim = time.time()
    sims = util.cos_sim(doc_embedding, embeddings)[0].cpu().numpy()
    top_indices = sims.argsort()[-top_k:][::-1]
    summary = " ".join([sentences[i] for i in sorted(top_indices)])
    end_sim = time.time()

    total_time = (time.time() - start)*1000
    embed_time = (end_embed - start_embed)*1000
    sim_time = (end_sim - start_sim)*1000

    return summary, {"total_ms": total_time, "embedding_ms": embed_time, "similarity_ms": sim_time}

def classify(text):
    start = time.time()
    vec = embedding_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    category = classifier.predict(vec)[0]
    end = time.time()
    return category, (end - start)*1000

# -----------------------------
# 3. Pipeline function
# -----------------------------
def process_article(text):
    summary, summary_times = summarize(text)
    category, classify_time = classify(text)
    times = {
        "summary_total_ms": summary_times["total_ms"],
        "embedding_ms": summary_times["embedding_ms"],
        "similarity_ms": summary_times["similarity_ms"],
        "classification_ms": classify_time
    }
    return {"summary": summary, "category": category, "times": times}

# -----------------------------
# 4. Example usage
# -----------------------------
example_text = "Vilniaus rajone pareigūnai sulaikė įtariamą narkotikų platintoją. Tai dalis didesnės operacijos kovojant su nusikalstamumu."

example_text = """
Nuo šių metų sausio 1-os dienos į Narkotinių ir psichotropinių medžiagų sąrašą įtrauktas muscimolis ir iboteninė rūgštis. Tai – pagrindinės paprastųjų musmirių psichoaktyvios medžiagos. Pastaraisiais metais Lietuvoje daugėjo apsinuodijimų šiuo nuodingu grybu, nes socialiniuose tinkluose buvo platinama informacija apie tariamą musmirių naudą bei jomis prekiaujama.

Šių medžiagų įtraukimas į narkotikų sąrašą reiškia, kad nuo šiol už musmirių turėjimą grės baudžiamoji atsakomybė. Sąraše esančios medžiagos draudžiamos vartoti, išskyrus atvejus, kai jos registruotos vaistinio preparato sudėtyje.

Tuo atveju, jei žmonės sugalvotų rinkti musmires savam vartojimui, įkliuvę policijai jie būtų baudžiami pagal BK 259 str., kur numatyta atsakomybė už narkotinių ir psichotropinių medžiagų disponavimą be tikslo jas platinti. 

Tuomet jis būtų baudžiamas bauda arba areštu, arba laisvės atėmimu iki dvejų metų. O jei musmirės būtų renkamos norint jas parduoti ar kitaip platinti, tuomet, priklausomai nuo surinkto kiekio, gali grėsti netgi laisvės atėmimas iki 15 metų. Be to, bus nebegalima rašyti apie tariamą musmirių naudą, nes pagal Visuomenės informavimo įstatymą draudžiama skelbti informaciją, kur propaguojamos ar reklamuojamos narkotinės ar psichotropinės medžiagos.
Daugėjo apsinuodijimų

Pastaraisiais metais internete plito informacija, neva raudonosios musmirės išgydo nepagydomas ligas, vėžį, padeda užmigti ir teikia kitokių naudų. Kartu populiarėja ir prekyba musmirėmis bei įvairiais jų produktais.

Atsirado net ir jų kontrabandos atvejų, pavyzdžiui, pernai muitinėje iš Baltarusijos sulaikyta beveik 200 kilogramų musmirių siunta.

Išties paprastoji musmirė pasižymi nuodingomis savybėmis, nes joje yra toksiškų medžiagų, kurios gali sukelti pilvo skausmus, pykinimą, viduriavimą, haliucinacijas ir kt. Ūmus simptomai ne visada pasireiškia, nes tam turi įtakos žmonių fiziologiniai skirtumai, be to, paprastojoje musmirėje susikaupia skirtingas toksiškų medžiagų kiekis.

Toksikologai jau seniai kalbėjo, kad jiems tenka gydyti vis daugiau raudonosiomis musmirėmis apsinuodijusių žmonių.

Gydytoja toksikologė Gabija Laubner-Sakalauskienė anksčiau yra skelbusi, kad kiekvieną rudenį rekordus skina apsinuodijimai grybais.

„Šiemet „ant bangos“ visokie „grybautojų“ forumai ir grupės, kuriose skelbiama informacija labai toli nuo teisybės. Kuri ne tik klaidina, bet realiai gali rimtai susargdinti ar net pražudyti.

Savaitės bėgyje mūsų ligoninėje dėl labai sunkios būklės gydyti du žmonės, kurie suvalgė raudonųjų musmirių .

Jų būklei pagerėjus, klausiau kodėl jie jų valgė. Atsakymai buvo nuo „mačiau reportažą per TV, kur Jūs kalbate apie musmirių žalą, bet nepatikėjau kad „tokios mažos raudonosios musmirės gali padaryti kažką blogo“ iki „internete rašo, kad jie gerina miegą, apsaugo nuo ligų ir išgydo vėžį“.“, - yra skelbusi toksikologė.
"""

result = process_article(example_text)
print(result)

end_total = time.time()
print(f"Total pipeline time: {(end_total - start_total)*1000:.1f} ms")

