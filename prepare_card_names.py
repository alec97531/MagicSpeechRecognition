import json
import re

def extract_cards(file_in):
    with open(file_in, 'r', encoding="utf-8") as fi:
        card_data = json.load(fi)
    return card_data

def pluck_card_data(card_data):
    card_data = [{"name":x["name"], "true_name":x['name'], "url":x['scryfall_uri']} for x in card_data]
    return card_data

def handle_split_cards(card_data):
    expanded_cards = []
    for card in card_data:
        name = card['name']
        # find split cards with "//"
        pattern = r"(.*?)\/\/(.*)"
        match = re.search(pattern, name)
        if match:
            newcard_1 = card
            newcard_1['name'] = match.group(1).strip()
            newcard_2 = card
            newcard_2['name'] = match.group(2).strip()
            expanded_cards.append(newcard_1)
            expanded_cards.append(newcard_2)
        else:
            expanded_cards.append(card)
    return expanded_cards

def clean_up_name(card_data):
    card_name = card_data['name']
    card_name = card_name.strip()
    card_name = card_name.lower()
    card_data['name'] = card_name
    return card_data

def clean_up_names(card_data):
    return [clean_up_name(x) for x in card_data]

def clean_up_dupes(card_names):
    return list(set(card_names))

def remove_arena_cards(card_data):
    # cards that start with "a-"
    pattern = r"^a-"
    return filter_names(pattern, card_data)

def filter_names(pattern, card_data):
    filtered_cards = []
    for card_datum in card_data:
        match = re.search(pattern, card_datum['name'])
        if not match:
            filtered_cards.append(card_datum)
    return filtered_cards

def key_by_name(card_data):
    return {x['name']: x for x in card_data}            

def load_names(file_out, data):
    with open(file_out, "w") as json_file:
        json.dump(data, json_file)

if __name__ == "__main__":
    cards=extract_cards("oracle-cards.json")
    print(f"extracted {len(cards)}")

    EXCLUDED_SET_TYPES = ["token", "memorabilia"]
    cards = [x for x in cards if x['set_type'] not in EXCLUDED_SET_TYPES]
    print(f"trimmed tokens: {len(cards)}")



    card_data = pluck_card_data(cards)
    print(f"plucked {len(card_data)}")
    card_data = remove_arena_cards(card_data)
    print(f"removed arena cards {len(card_data)}")
    card_data= handle_split_cards(card_data)
    print(f"split to {len(card_data)}")
    card_data = clean_up_names(card_data)
    card_data = key_by_name(card_data)
    print(f"loading {len(card_data)}")
    load_names("cardnames.json", card_data)