"""Builds the classifier dataset.

Real data: the public SMS Spam Collection (spam -> Promotional, ham -> Normal).
Generated data: emails for Urgent, Opportunity and Meeting, plus extra Promotional/Normal.
The test split uses DIFFERENT templates from training, so the score reflects unseen wording.

Run:  python ml/data/build_dataset.py
"""
import csv
import random
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
SMS_URL = "https://raw.githubusercontent.com/justmarkham/pycon-2016-tutorial/master/data/sms.tsv"
LABELS = ["Urgent", "Opportunity", "Meeting", "Promotional", "Normal"]

FILL = {
    "name": ["Priya", "Rahul", "Ananya", "Vikram", "Sarah", "John", "Meera", "Arjun", "Neha", "David"],
    "company": ["Infosys", "Razorpay", "Zomato", "Microsoft", "Swiggy", "Atlassian", "Flipkart", "Google", "a fintech startup", "our team"],
    "role": ["Backend Engineer", "ML Engineer", "SDE Intern", "AI Engineer", "Full Stack Developer", "Data Scientist"],
    "day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "tomorrow", "next week"],
    "time": ["10 AM", "11:30 AM", "2 PM", "4 PM", "5:30 PM"],
    "thing": ["the quarterly report", "the project proposal", "the invoice", "the design doc", "the client deck", "the test results"],
    "product": ["headphones", "sneakers", "laptops", "the premium plan", "smart watches", "online courses"],
    "pct": ["20", "30", "40", "50", "70"],
    "topic": ["the sprint plan", "the product roadmap", "Q3 targets", "the launch", "hiring", "the budget"],
}

# Each email is assembled from random phrases, so the model learns meaning-carrying words rather
# than memorising whole templates. Every bank is split: the first 75% of phrases are used for
# training and the last 25% ONLY for testing, so the test score reflects wording it never saw.
GREETINGS = ["Hi {name},", "Hello,", "Hey {name},", "Dear {name},", "Hi team,", "Good morning,", ""]
CLOSINGS = ["Thanks,", "Regards,", "Best,", "Cheers,", "Thank you.", "", "Let me know."]
NEUTRAL = [
    "Hope you're doing well.", "Hope your week is going well.", "Quick note below.",
    "Copying {name} for visibility.", "Sharing some context.", "Following up on my earlier mail.",
]

BANKS = {
    "Urgent": {
        "subjects": [
            "URGENT: {thing}", "Action required today", "Immediate attention needed", "Deadline today",
            "Critical: production issue", "Overdue: {thing}", "Time sensitive request", "Escalation",
            "Final reminder", "Need this ASAP", "High priority: {thing}", "Account suspension notice",
        ],
        "phrases": [
            "We need {thing} by end of day today.", "Please treat this as top priority.",
            "The production server is down and customers are affected.", "This is blocking the release.",
            "Please respond immediately.", "It is overdue and the client is escalating.",
            "Missing this deadline will cost us the contract.", "There's a critical bug in checkout.",
            "Please fix this as soon as possible.", "We have less than an hour to resolve this.",
            "Your password must be reset immediately.", "Your account will be suspended within 24 hours.",
            "Payment is overdue, please clear it today.", "This cannot wait until tomorrow.",
            "The outage is getting worse, all hands needed.", "Need your sign-off right now.",
            "Late submissions will not be accepted.", "The portal closes tonight.",
            "We are losing customers every minute this is down.", "Drop everything and look at this.",
        ],
    },
    "Opportunity": {
        "subjects": [
            "Interview invitation", "Job opportunity at {company}", "Your application update",
            "Offer letter: {role}", "Internship opening", "We'd love to talk", "{role} position",
            "Shortlisted for the next round", "Recruiter from {company}", "Career opportunity",
            "Congratulations on your selection", "Open role on our team",
        ],
        "phrases": [
            "We'd like to invite you to interview for the {role} role.", "We are hiring a {role}.",
            "Your profile looks like a great fit for our team.", "Are you open to new opportunities?",
            "Your application has been shortlisted.", "We are pleased to offer you the position.",
            "Please find your offer letter attached.", "I'm a recruiter at {company}.",
            "Your projects on GitHub caught our attention.", "The role offers a competitive salary.",
            "You have cleared the online assessment.", "Let's schedule your technical interview round.",
            "We have an internship opening this summer.", "Our hiring manager wants to speak with you.",
            "You've been selected for the internship programme.", "We're building an AI team and want you on it.",
            "Your experience with FastAPI matches what we need.", "Apply before the deadline to be considered.",
            "HR will share the joining formalities.", "Would you consider joining {company}?",
        ],
    },
    "Meeting": {
        "subjects": [
            "Meeting on {day}", "Invitation: {topic} sync", "Can we schedule a call?", "Rescheduled: standup",
            "Agenda for {day}", "Zoom link for {topic}", "Calendar invite", "1:1 this week",
            "Catch up {day}?", "Moving our call", "{topic} review session", "Quick sync",
        ],
        "phrases": [
            "Let's meet on {day} at {time} to discuss {topic}.", "I've sent a calendar invite.",
            "Could we schedule a quick call {day}?", "The standup is moved to {time}.",
            "Here is the agenda for our meeting.", "Join using the Google Meet link.",
            "Sharing the Zoom link for our discussion.", "Does {time} on {day} work for you?",
            "Please accept the invite.", "Let's sync for 30 minutes on {topic}.",
            "Can we move our call to {day}?", "I've booked the conference room.",
            "Our 1:1 is shifted to {day}.", "Please bring your slides to the review.",
            "Let me know a time slot that suits you.", "We'll walk through {topic} in the meeting.",
            "Are you free {day} afternoon for a call?", "Let's set up a weekly check-in.",
            "Dial-in details are in the invite.", "I'll send the meeting notes after the call.",
        ],
    },
    "Promotional": {
        "subjects": [
            "{pct}% off {product}", "Exclusive deal for you", "Our monthly newsletter", "Flash sale is live",
            "You've won a free gift", "Last chance: big savings", "Members save {pct}%", "Weekly digest",
            "New arrivals just dropped", "Limited time offer", "Mega sale starts now", "Get 3 months free",
        ],
        "phrases": [
            "Shop now and get {pct}% off {product}.", "Limited stock, offer ends Sunday.",
            "Use code SAVE{pct} at checkout.", "Unsubscribe anytime.", "Free shipping on all orders.",
            "Click here to claim your prize.", "Hurry, while stocks last.", "Biggest discounts of the year.",
            "Upgrade to Pro and get three months free.", "Top stories picked for you this week.",
            "To stop receiving these emails, unsubscribe here.", "Don't miss out on huge savings.",
            "You've been selected for a lucky draw.", "Earn cashback on {product}.",
            "New arrivals in {product} are here.", "Exclusive offer for subscribers only.",
            "Rate us and win vouchers.", "Buy one get one free this weekend.",
            "Your cart is waiting, complete your order.", "Download our app for extra discounts.",
        ],
    },
    "Normal": {
        "subjects": [
            "Notes from today", "Thanks!", "Weekend plans", "FYI", "Photos from the trip", "Quick update",
            "Re: {thing}", "Lunch?", "Great job", "Book recommendation", "Happy birthday!", "Hello",
        ],
        "phrases": [
            "Sharing my notes from today, no action needed.", "Thanks for helping with {thing}.",
            "Are you around this weekend?", "Just keeping you in the loop.", "Here are the photos from the trip.",
            "Everything is on track.", "Got it, thanks.", "Want to grab lunch around 1?",
            "The demo went really well today.", "Finished the book you suggested, loved it.",
            "Happy birthday, have a great year ahead!", "Hope the family is doing well.",
            "No rush on this, just sharing.", "That was a fun evening, let's do it again.",
            "I'll take a look when I get a chance.", "Nice work on the presentation.",
            "The weather here has been lovely.", "Let me know how the trip goes.",
            "Saw this article and thought of you.", "All good on my side.",
        ],
    },
}


def _split(items: list[str], split: str) -> list[str]:
    cut = max(1, int(len(items) * 0.75))
    return items[:cut] if split == "train" else items[cut:]


def fill(text: str, rng: random.Random) -> str:
    return text.format(**{k: rng.choice(v) for k, v in FILL.items()})


def generate(split: str, per_label: int, rng: random.Random) -> list[dict]:
    rows = []
    for label, bank in BANKS.items():
        subjects, phrases = _split(bank["subjects"], split), _split(bank["phrases"], split)
        for _ in range(per_label):
            body = [rng.choice(GREETINGS)]
            if rng.random() < 0.4:
                body.append(rng.choice(NEUTRAL))
            body += rng.sample(phrases, k=min(len(phrases), rng.randint(1, 3)))
            body.append(rng.choice(CLOSINGS))
            rows.append({
                "subject": fill(rng.choice(subjects), rng),
                "body": fill(" ".join(b for b in body if b), rng),
                "label": label, "source": "generated",
            })
    return rows


def load_sms(rng: random.Random) -> list[dict]:
    cache = HERE / "raw" / "sms.tsv"
    if not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        print("Downloading SMS Spam Collection…")
        urllib.request.urlretrieve(SMS_URL, cache)
    rows = []
    with open(cache, encoding="utf-8") as f:
        for kind, text in csv.reader(f, delimiter="\t"):
            label = "Promotional" if kind == "spam" else "Normal"
            rows.append({"subject": "", "body": text, "label": label, "source": "sms"})
    spam = [r for r in rows if r["label"] == "Promotional"]
    ham = rng.sample([r for r in rows if r["label"] == "Normal"], 300)  # don't let Normal swamp the rest
    return spam + ham


def write(path: Path, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["subject", "body", "label", "source"])
        w.writeheader()
        w.writerows(rows)


def main():
    rng = random.Random(42)
    sms = load_sms(rng)
    rng.shuffle(sms)
    cut = int(len(sms) * 0.8)
    train = generate("train", 500, rng) + sms[:cut]
    test = generate("test", 80, rng) + sms[cut:]
    rng.shuffle(train)
    write(HERE / "train.csv", train)
    write(HERE / "test.csv", test)
    print(f"train: {len(train)} rows, test: {len(test)} rows")
    for label in LABELS:
        print(f"  {label:12} train={sum(r['label'] == label for r in train):5}  test={sum(r['label'] == label for r in test):4}")


if __name__ == "__main__":
    main()
