**En résumé :**
Haystack 3.x n’embarque pas une « mémoire magique » à l’intérieur du modèle ; il fournit plutôt un **contrat de données** (`ChatMessage`) et trois **composants opt-in** (`ChatMessageWriter`, `ChatMessageRetriever`, `ChatMessageStore`) pour que *toi* choisisses où et comment conserver l’historique.

* *À court terme* l’`Agent` garde simplement une liste Python de `ChatMessage` qu’il réinjecte dans le prompt à chaque tour.
* *À long terme* tu branches un **store** (en RAM, Redis, Base SQL, etc.) via l’API `ChatMessageStore`; Haystack fournit par défaut `InMemoryChatMessageStore` et laisse l’interface ouverte pour tes propres back-ends.
* Pour ne pas dépasser la fenêtre de contexte, Haystack offre des stratégies de **fenêtrage** et un composant de **résumé incrémental** (`ConversationSummaryMemory`) que tu peux ajouter dans le pipeline.
  Ainsi, la persistance, le nettoyage et la compression de la mémoire sont totalement configurables – rien d’imposé ni de caché.

---

## 1. Modèle de mémoire : des `ChatMessage` partout !

1. Chaque fragment de dialogue (user, assistant, tool, système…) est encapsulé dans la dataclass `ChatMessage` ; c’est l’unité qu’un générateur de type *chat* attend et qu’il renvoie ([Haystack Documentation][1]).
2. Quand tu appelles `agent.run(messages=[...])`, tu lui passes l’historique complet ou partiel ; l’`Agent` se contente ensuite d’ajouter le nouveau message à la liste avant de rendre la main ([Haystack Documentation][2]).
3. Si tu ne fais rien de plus, la « mémoire » vit seulement le temps du processus Python.

---

## 2. Deux couches de stockage

| Couche                  | Objet & rôle                                                                                                                                                                                                                                      | Scope par défaut                   |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **Mémoire volatile**    | La variable `messages` (liste de `ChatMessage`) que l’agent réinjecte à chaque tour (« memory injection ») ([Haystack][3])                                                                                                                        | Session courante                   |
| **Mémoire persistante** | Implémentations de `ChatMessageStore` (RAM, Redis, SQL…) pilotées par deux composants :<br>  • `ChatMessageWriter` : écrit dans le store ([Haystack Documentation][4])<br>  • `ChatMessageRetriever` : lit et filtre l’historique ([Haystack][5]) | Entre les sessions / multi-process |

Le couple *writer / retriever* est branché exactement comme n’importe quel autre composant dans une pipeline ou un agent ; aucune magie supplémentaire.

---

## 3. Composants disponibles prêts à l’emploi

| Composant                   | Paquet                              | Utilité clé                                                                                |
| --------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------------ |
| `InMemoryChatMessageStore`  | `haystack-experimental`             | Prototypage rapide sans infra ([PyPI][6])                                                  |
| `ChatMessageWriter`         | `haystack-experimental`             | Sérialise une liste de messages vers le store ([Haystack Documentation][4])                |
| `ChatMessageRetriever`      | `haystack-experimental`             | Récupère les derniers *n* messages ou applique un filtre utilisateur/temps ([Haystack][5]) |
| `ConversationSummaryMemory` | core (`haystack.components.memory`) | Résume la conversation tous les *k* tours pour tenir dans le contexte ([GitHub][7])        |

Des projets tiers proposent déjà un **RedisChatMessageStore**, une mémoire « travail/sensorielle » ou un store vecteur pour faire de la recherche dans l’historique ([GitHub][8]) ([Reddit][9]).

---

## 4. Gérer la taille : fenêtres & résumés

* **Fenêtre glissante** : limite simplement le nombre de messages renvoyés par le retriever (ex. `window=20`).
* **Résumé incrémental** : `ConversationSummaryMemory` appelle un LLM pour condenser les *k* derniers échanges et stocke la synthèse comme un `ChatMessage` séparé ; la taille du prompt reste stable quelle que soit la durée de la session ([Matteo Villosio Personal Blog][10]).
* **RAG conversatif** : combine `ChatMessageRetriever` (historique) + retriever documentaire → les deux listes sont fusionnées dans un `PromptBuilder` avec deux variables (`memories`, `documents`) ([Medium][11]).

---

## 5. Exemple minimal complet

```python
from haystack.components.agents import Agent
from haystack_experimental.chat_message_stores.in_memory import InMemoryChatMessageStore
from haystack_experimental.components.writers import ChatMessageWriter
from haystack_experimental.components.retrievers import ChatMessageRetriever
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.dataclasses import ChatMessage

# 1) Store + I/O components
store      = InMemoryChatMessageStore()
writer     = ChatMessageWriter(store)
retriever  = ChatMessageRetriever(store, window=15)

# 2) Agent avec générateur chat
agent = Agent(
    chat_generator=OpenAIChatGenerator(model="gpt-4o-mini"),
    system_prompt="Tu es le PNJ tavernier, serviable mais sarcastique."
)

# 3) Boucle de jeu
while True:
    user_input = input("> ")
    # Lire l’historique utile
    memories = retriever.run(user_id="player")["memories"]
    # Construire la nouvelle requête
    messages = memories + [ChatMessage.from_user(user_input, metadata={"user_id": "player"})]
    result   = agent.run(messages=messages)
    # Afficher & persister
    print(result["messages"][-1].text)
    writer.run(messages=[messages[-2], messages[-1]])
```

Tout tient en \~40 lignes : le tavernier se souvient d’une fenêtre de 15 messages et peut résumer si tu ajoutes `ConversationSummaryMemory` en amont.

---

## 6. Bonnes pratiques

1. **Séparer le *store* de l’agent** : facile à échanger (Redis en prod, RAM en test).
2. **Indexer en vectoriel l’historique long** si tu veux rechercher des thèmes anciens (ex. souvenirs de quêtes).
3. **Filtrer ou anonymiser** avant d’écrire dans la base si tu stockes des données sensibles.
4. **Tester les coûts** : chaque résumé = un appel LLM ; règle `k` selon ton budget.
5. **Tracer** : Ajoute un `ChatMessageWriter` vers Argilla ou Langfuse pour rejouer/debugger tes sessions ([PyPI][12]) ([Stack Overflow][13]).

---

### Pour aller plus loin

* Notebook **Conversational RAG using Memory** (Cookbook) : tutoriel pas-à-pas avec les trois composants mémoire ([Haystack][5]).
* Article *5 Levels of Building Chatbot Apps – Level 2* : démo d’un chatbot mémoire-plus-RAG en <200 lignes ([Medium][14]).
* Vidéo *Working Memory Agents & Haystack* pour une explication visuelle des design patterns ([YouTube][15]).
* Blog *Good Listener – How Memory Enables Conversational Agents* pour la philosophie derrière l’injection de mémoire ([Haystack][3]).

Avec ces briques, tu contrôles pleinement ce que ton agent retient, combien de temps et sous quelle forme – idéal pour garder tes joueurs immergés sans saturer le contexte du LLM !

[1]: https://docs.haystack.deepset.ai/docs/chatmessage?utm_source=chatgpt.com "ChatMessage - Haystack Documentation - Deepset"
[2]: https://docs.haystack.deepset.ai/v1.22/docs/agent?utm_source=chatgpt.com "Agent - Haystack Documentation"
[3]: https://haystack.deepset.ai/blog/memory-conversational-agents?utm_source=chatgpt.com "Good Listener: How Memory Enables Conversational Agents"
[4]: https://docs.haystack.deepset.ai/reference/experimental-writers-api?utm_source=chatgpt.com "Writers - Haystack Documentation - Deepset"
[5]: https://haystack.deepset.ai/cookbook/conversational_rag_using_memory?utm_source=chatgpt.com "Conversational RAG using Memory - Haystack - Deepset"
[6]: https://pypi.org/project/haystack-experimental/?utm_source=chatgpt.com "haystack-experimental - PyPI"
[7]: https://github.com/deepset-ai/haystack/issues/5091?utm_source=chatgpt.com "Provide option to create the summary of the whole conversation ..."
[8]: https://github.com/rolandtannous/haystack-memory?utm_source=chatgpt.com "Basic Memory library for Haystack NLP agents - GitHub"
[9]: https://www.reddit.com/r/LocalLLaMA/comments/1gvhpjj/agent_memory/?utm_source=chatgpt.com "Agent Memory : r/LocalLLaMA - Reddit"
[10]: https://matteovillosio.com/post/unofficial-haystack-doc-agent/?utm_source=chatgpt.com "Enhancing Your Haystack Experience: The Unofficial Chatbot Guide"
[11]: https://medium.com/%40dharmamst/retrieval-augmented-generation-rag-chatbot-for-documents-with-haystack-6a3f115bc31b?utm_source=chatgpt.com "Retrieval Augmented Generation(RAG) — Chatbot for documents ..."
[12]: https://pypi.org/project/argilla-haystack/?utm_source=chatgpt.com "argilla-haystack - PyPI"
[13]: https://stackoverflow.com/questions/78282522/how-to-use-googleaigeminichatgenerator-for-haystack-with-googles-gemini?utm_source=chatgpt.com "How to Use GoogleAIGeminiChatGenerator for Haystack with ..."
[14]: https://medium.com/%40armantunga/5-levels-of-building-chatbot-apps-with-haystack-level-2-437a207ae784?utm_source=chatgpt.com "5 Levels of Building Chatbot Apps with Haystack — Level 2 - Medium"
[15]: https://www.youtube.com/watch?v=8WhX9DZBrmY&utm_source=chatgpt.com "Working Memory Agents and Haystack Framework | Generative AI"
