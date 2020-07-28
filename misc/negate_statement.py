import spacy

from pattern import en

MODALS = {'will', 'shall'}


def main():
    nlp = spacy.load("en_core_web_sm")
    sentence = input("Enter a sentence, or Q to stop:\n")

    while sentence != "Q":
        neg = negate_last_verb(nlp, sentence)

        if neg is None:
            print("Error")
        else:
            print(neg)

        sentence = input("Enter a sentence, or Q to stop:\n")


def negate_last_verb(nlp, statement):
    """
    Takes a statement and negates it
    :param statement: string statement
    :return: the negated statement
    """
    try:
        doc = [t for t in nlp(statement)]
        last_verb_index = [i for i, t in enumerate(doc) if t.pos_ == "VERB"][-1]
        token = doc[last_verb_index]
        morph_features = nlp.vocab.morphology.tag_map[token.tag_]
        new_verb = negate(token, morph_features)
        tokens = [t.text for t in doc]
        tokens[last_verb_index] = new_verb
        return " ".join(tokens)
    except:
        return None


def negate(token, morph_features):
    """
    Get a head verb and negate it
    :param token: the SpaCy token of the main verb
    :param morph_features: SpaCy `nlp.vocab.morphology.tag_map`
    :return: the negated string or None if failed to negate
    """
    verb = token.text
    tense = morph_features.get('Tense', None)
    person = morph_features.get("Person", 3)
    number = {"sing": en.SG, "plur": en.PL}.get(morph_features.get("Number", "sing"))
    auxes = [t for t in token.lefts if t.dep_ == 'aux' or t.lemma_ in {"be", "have"}]

    # ing: add not after the have/be verb or future: add "not" after the modal
    if (token.tag_ == "VBG" and len(auxes) > 0) or is_future_tense(token):
        return "not " + token.text

    # Present simple or past
    elif tense in {"pres", "past"}:
        aux_tense = {"pres": en.PRESENT, "past": en.PAST}[tense]

        if token.lemma_ == "be":
            return " ".join((verb, "not"))

        else:
            aux = en.conjugate("do",
                               tense=aux_tense,
                               person=person,
                               number=number,
                               parse=True)

            verb = en.conjugate(verb,
                                tense=en.INFINITIVE,
                                person=person,
                                number=number,
                                parse=True)

            return " ".join((aux, "not", verb))

    else:
        return None


def is_future_tense(token):
    """
    Is this verb with a future tense?
    :param token: SpaCy token
    :return: Is this verb with a future tense?
    """
    return token.tag_ == 'VB' and any([t.text in MODALS and t.dep_ == 'aux' for t in token.lefts])


if __name__ == '__main__':
    main()
