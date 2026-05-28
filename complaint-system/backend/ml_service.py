import os
import re
import pickle
from difflib import get_close_matches
from typing import Tuple

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    from nltk.tokenize import word_tokenize
    for pkg in ["punkt", "stopwords", "wordnet", "omw-1.4", "punkt_tab"]:
        nltk.download(pkg, quiet=True)
    _stop_words = set(stopwords.words("english"))
    _lemmatizer = WordNetLemmatizer()
    _NLTK_AVAILABLE = True
except Exception:
    _NLTK_AVAILABLE = False

BASE_DIR = os.path.dirname(__file__)

_VOCAB = {
    "account","login","password","hack","hacked","unauthorized","locked",
    "phishing","blocked","access","otp","signin",
    "delivery","delivered","deliver","shipment","shipping","tracking",
    "courier","dispatch","parcel","arrived","received",
    "payment","charged","charge","deducted","overcharged","billing",
    "transaction","declined","upi","banking","wallet","debit",
    "refund","double","cashback","reimbursement",
    "damaged","broken","defective","cracked","scratched","faulty",
    "poor","useless","quality",
    "wrong","incorrect","mismatch","missing",
    "rude","unhelpful","support","agent","representative",
    "stock","available","availability","restock",
    "fraud","stolen","scam","urgent","critical","dangerous","safety",
    "not","working","order","product","item",
}


def _fuzzy_correct(text: str) -> str:
    words = text.lower().split()
    corrected = []
    for word in words:
        clean = re.sub(r"[^a-z]", "", word)
        if len(clean) >= 5 and clean not in _VOCAB:
            matches = get_close_matches(clean, _VOCAB, n=1, cutoff=0.82)
            corrected.append(matches[0] if matches else word)
        else:
            corrected.append(word)
    return " ".join(corrected)


def _preprocess(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", "", text)
    if _NLTK_AVAILABLE:
        tokens = word_tokenize(text)
        cleaned = [_lemmatizer.lemmatize(w) for w in tokens if w not in _stop_words]
        return " ".join(cleaned)
    basic_stops = {"the","a","an","is","it","in","of","and","to","i","my","was","not","for","on","with"}
    return " ".join(w for w in text.split() if w not in basic_stops)

_ft_model = None
_FT_READY  = False

try:
    import fasttext
    _ft_path = os.path.join(BASE_DIR, "complaint_fasttext.bin")
    if os.path.exists(_ft_path):
        fasttext.FastText.eprint = lambda x: None
        _ft_model = fasttext.load_model(_ft_path)
        _FT_READY = True
        print("[ML Service] FastText model loaded OK")
    else:
        print("[ML Service] complaint_fasttext.bin not found – run train_fasttext.py to generate it.")
except ImportError:
    print("[ML Service] fasttext not installed – run: pip install fasttext-wheel")
except Exception as e:
    print(f"[ML Service] FastText load error: {e}")


def _load(fname: str):
    path = os.path.join(BASE_DIR, fname)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    return None

_cat_model  = _load("category_model.pkl")
_cat_le     = _load("category_encoder.pkl")
_prio_model = _load("priority_model.pkl")
_prio_le    = _load("priority_encoder.pkl")
_SKLEARN_READY = all(x is not None for x in [_cat_model, _cat_le, _prio_model, _prio_le])

if _SKLEARN_READY:
    print("[ML Service] sklearn fallback models loaded OK")
else:
    print("[ML Service] sklearn models not found – pure rule-based fallback active.")

_FT_LABEL_DISPLAY = {
    "account_issue":    "Account Issue",
    "customer_service": "Customer Service",
    "delivery_issue":   "Delivery Issue",
    "refund_request":   "Refund Request",
    "product_issue":    "Product Issue",
    "product_inquiry":  "Product Inquiry",
    "payment_issue":    "Payment Issue",
}

_SKLEARN_DISPLAY = {
    "Account Issue":    "Account Issue",
    "Customer Service": "Customer Service",
    "Delivery Issue":   "Delivery Issue",
    "Refund Request":   "Refund Request",
    "Product Issue":    "Product Issue",
    "Product Inquiry":  "Product Inquiry",
    "Payment Issue":    "Payment Issue",
    "Wrong Item":       "Product Issue",
    "Damaged Product":  "Product Issue",
    "Delivery Delay":   "Delivery Issue",
    "Poor Customer Service": "Customer Service",
}

_CATEGORY_RULES = {
    "Account Issue": [
        "account","hacked","unauthorized","password","login","account","access",
        "phishing","locked","suspend","sign in","blocked account","account blocked",
        "account suspended","account hacked",
        "reset password","two factor","2fa","security breach",
    ],
    "Payment Issue": [
        "payment","payment not processed","payment declined",
        "transaction failed","transaction not processed",
        "double charge","double charged","duplicate charge",
        "extra charge","extra amount","wrong amount charged",
        "amount deducted","deducted from account",
        "deducted from wallet","bank deducted",
        "upi payment","net banking failed","wallet deducted",
        "billing error","billing issue",
        "wallet balance gone","wallet amount","amount taken",
        "money gone","money removed","funds removed",
        "amount removed","taken from wallet","taken from account",
        "debited without","charged without","deducted without",
        "someone took money","balance deducted","balance gone",
        "funds","emptied","balance missing",
        "amount missing","stolen from","money stolen",
    ],
    "Refund Request": [
        "refund","money back","reimburs","cashback","cash back",
        "refund not received","refund pending","refund denied",
        "refund not processed","want refund","need refund",
        "process refund","where is my refund",
    ],
    "Product Issue": [
        "damaged","broken","defective","defect","crack","cracked","scratch",
        "not working","stopped working","faulty","poor quality",
        "useless","damaged product","product broken",
        "came damaged","manufacturing defect",
        "dead on arrival","doa",
        "wrong item","wrong product","incorrect item","different item","mismatch",
        "wrong size","wrong color","got wrong","sent wrong",
        "wrong order","different product","item missing",
        "incomplete order","part missing",
    ],
    "Delivery Issue": [
        "delivery","deliver","delivered","not delivered","never delivered",
        "shipping","tracking","courier","dispatch","dispatched",
        "late","delay","delayed","not arrived","not received",
        "out for delivery","stuck in transit","lost in transit",
        "where is my package","package not received",
        "delivery not done",
    ],
    "Product Inquiry": [
        "availability","when will","restock","restocked",
        "when is it available","out of stock",
        "pre-order","preorder","launch date","release date",
        "coming soon","when available","in stock",
    ],
    "Customer Service": [
        "customer service","support","agent","representative","executive",
        "unhelpful","no reply","not responding","complaint ignored",
        "poor service","worst service","very bad experience",
        "did not help","nobody responded","slow response",
        "nobody called back",
    ],
}

_RULE_PRIORITY_CATEGORIES = {"Payment Issue", "Product Inquiry"}

_PRIORITY_RULES = {
    "High": [
        "hack","hacked","fraud","unauthorized","stolen","security breach",
        "emergency","urgent","critical","money stolen","account compromised",
        "someone else","suspicious login","identity theft",
        "account locked","blocked","access denied",
        "double charge","double charged","duplicate charge",
        "money deducted","amount deducted","bank deducted",
        "payment failed","card declined","transaction failed",
        "money taken","money gone","funds removed",
        "balance gone","amount taken","taken from wallet",
        "stolen from","money stolen","wallet","funds","emptied",
        "not delivered","completely broken","dead on arrival",
        "broken product","defective","faulty","useless",
        "wrong product","lawsuit","escalate","dangerous",
        "safety","refund denied","refund rejected",
    ],
    "Medium": [
        "delay","delayed","tracking","slow response","waiting",
        "poor quality","bad quality","refund pending",
        "wrong size","wrong color","missing item",
    ],
    "Low": [
        "inquiry","question","feedback","minor","small","suggestion",
        "exchange","return","general","when will","in stock",
    ],
}

_CATEGORY_MIN_PRIORITY = {
    "Account Issue":         "High",
    "Product Issue":         "Medium",
    "Payment Issue":         "High",
    "Refund Request":        "Medium",
    "Delivery Issue":        "Medium",
    "Customer Service":      "Low",
    "Product Inquiry":       "Low",
    "Damaged Product":       "Medium",
    "Delivery Delay":        "Medium",
    "Poor Customer Service": "Low",
}

_PRIORITY_ORDER = ["Low","Medium","High"]


def _rule_category(text: str) -> str:
    lower = _fuzzy_correct(text.lower())
    scores = {cat: sum(len(kw.split()) for kw in kws if kw in lower)
              for cat, kws in _CATEGORY_RULES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Customer Service"


def _rule_priority(text: str, category: str) -> str:
    lower = _fuzzy_correct(text.lower())
    kp = None
    for prio in ("High","Medium","Low"):
        for kw in _PRIORITY_RULES[prio]:
            if kw in lower:
                kp = prio
                break
        if kp: break
    floor = _CATEGORY_MIN_PRIORITY.get(category, "Medium")
    if kp is None:
        return floor
    return _PRIORITY_ORDER[max(_PRIORITY_ORDER.index(kp), _PRIORITY_ORDER.index(floor))]


def classify_complaint(complaint_text: str) -> Tuple[str, str]:
    corrected = _fuzzy_correct(complaint_text)
    cleaned   = _preprocess(corrected)

    rule_raw    = _rule_category(corrected)
    rule_display = _SKLEARN_DISPLAY.get(rule_raw, rule_raw)

    if rule_display in _RULE_PRIORITY_CATEGORIES:
        category = rule_display
    elif _FT_READY:
        labels, probs = _ft_model.predict(cleaned, k=1)
        ft_label = labels[0].replace("__label__", "")
        category = _FT_LABEL_DISPLAY.get(ft_label, ft_label.replace("_", " "))
    elif _SKLEARN_READY:
        cat_idx  = _cat_model.predict([cleaned])[0]
        cat_raw  = _cat_le.inverse_transform([cat_idx])[0]
        category = _SKLEARN_DISPLAY.get(cat_raw, cat_raw)
    else:
        category = rule_display

    priority = _rule_priority(corrected, category)
    return category, priority


def _extract_subject(text: str) -> str:
    openers = [
        r"^(i (have|am|want|need|would like to|am writing to) (complain|complaint|report|raise|flag) (about|regarding|for)?\s*)",
        r"^(my|the|their|your)\s+",
        r"^(i am complaining about|i want to complain about|i would like to complain about)\s*",
    ]
    cleaned = text.strip().rstrip("?.")
    for pattern in openers:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE).strip()
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned[:60] if len(cleaned) > 60 else cleaned


def get_resolution_advice(category: str, priority: str, complaint_text: str = "") -> str:
    subject = _extract_subject(complaint_text) if complaint_text else ""

    prefix = {
        "High":   "WARNING HIGH Priority - Escalated to our senior team.",
        "Medium": "Your request has been logged.",
        "Low":    "Thank you for reaching out.",
    }.get(priority, "Thank you for reaching out.")

    if category == "Account Issue":
        body = (
            "Our security team has been alerted. Please reset your password immediately "
            "and enable two-factor authentication. We'll investigate and secure your account within 24 hours."
        )
    elif category == "Payment Issue":
        ref = 'regarding "' + subject + '"' if subject else "for your payment"
        body = (
            "We have escalated your payment issue " + ref + " to our billing team. "
            "You'll receive a response within 24 hours. Please do not retry the payment."
        )
    elif category == "Refund Request":
        ref = 'regarding "' + subject + '"' if subject else "for your order"
        body = (
            "We have initiated a refund review " + ref + ". "
            "Refunds typically take 5-7 business days to process once approved."
        )
    elif category == "Delivery Issue":
        ref = 'for "' + subject + '"' if subject else "for your order"
        body = (
            "We have escalated your delivery concern " + ref + " to our courier partner. "
            "Please allow 1-2 business days for an update on your shipment."
        )
    elif category == "Product Issue":
        lower = complaint_text.lower()
        is_wrong = any(kw in lower for kw in ("wrong item","wrong product","incorrect item","different item","wrong size","wrong color","wrong order"))
        if is_wrong:
            ref = '"' + subject + '"' if subject else "your order"
            body = (
                "We are sorry you received the wrong item " + ref + ". "
                "Please keep it and our team will arrange a replacement or full refund within 48 hours."
            )
        else:
            ref = 'with "' + subject + '"' if subject else "with your product"
            body = (
                "We have flagged your product quality concern " + ref + ". "
                "Our team will review and contact you within 48 hours with a resolution."
            )
    elif category == "Customer Service":
        body = (
            "We sincerely apologise for your experience. Your feedback has been shared "
            "with our quality team and the relevant agent will be reviewed."
        )
    elif category == "Product Inquiry":
        ref = '"' + subject + '"' if subject else "the item you mentioned"
        body = (
            "We have checked availability for " + ref + ". "
            "Our team will update you on stock and pricing shortly."
        )
    elif category == "Wrong Item":
        ref = '"' + subject + '"' if subject else "your order"
        body = (
            "We are sorry about the wrong item you received " + ref + ". "
            "Please keep the item and our team will arrange a replacement or full refund within 48 hours."
        )
    else:
        body = (
            "Thank you for your complaint. Our team will review it and get back to you shortly."
        )

    return f"{prefix} {body}"
