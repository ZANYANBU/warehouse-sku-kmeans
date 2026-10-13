"""Presentation script for the Project Review 3 deck: one A4 page per slide,
three slides (three pages) per speaker, plus a cover and a glossary page."""
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

HERE = Path(__file__).parent
OUT = sys.argv[1] if len(sys.argv) > 1 else str(HERE / "script.pdf")

FONTS = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("Body", FONTS + "Arial.ttf"))
pdfmetrics.registerFont(TTFont("Body-Bold", FONTS + "Arial Bold.ttf"))
pdfmetrics.registerFont(TTFont("Body-Italic", FONTS + "Arial Italic.ttf"))
pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic", boldItalic="Body-Bold")

TEAL = colors.HexColor("#0F4C5C")
ORANGE = colors.HexColor("#F28C28")
GREEN = colors.HexColor("#2A9D8F")
ROSE = colors.HexColor("#D1495B")
SLATE = colors.HexColor("#5F7180")
TINT = colors.HexColor("#EAF2F3")
WARM = colors.HexColor("#FFF4E5")
INK = colors.HexColor("#16212B")
WHITE = colors.white

W, H = A4
M = 16 * mm
CW = W - 2 * M  # content width


def st(name, **kw):
    base = dict(fontName="Body", fontSize=11, leading=15.5, textColor=INK, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


BODY = st("body", fontSize=11.5, leading=16.5)
SAY = st("say", fontSize=12.5, leading=18.5)
SMALL = st("small", fontSize=9.5, leading=13, textColor=SLATE)
LABEL = st("label", fontName="Body-Bold", fontSize=9, leading=12, textColor=TEAL)
H1 = st("h1", fontName="Body-Bold", fontSize=19, leading=23, textColor=TEAL)
TERM = st("term", fontSize=10.3, leading=14)
BAND = st("band", fontName="Body-Bold", fontSize=12, leading=15, textColor=WHITE)
BAND_R = st("band_r", fontSize=10, leading=15, textColor=WHITE, alignment=2)
COVER_T = st("cover_t", fontName="Body-Bold", fontSize=26, leading=31, textColor=TEAL)
COVER_S = st("cover_s", fontSize=13, leading=18, textColor=INK)
CELL = st("cell", fontSize=10.5, leading=14)
CELL_B = st("cell_b", fontName="Body-Bold", fontSize=10.5, leading=14)
CELL_H = st("cell_h", fontName="Body-Bold", fontSize=10.5, leading=14, textColor=WHITE)

SPEAKERS = [
    ("V. Anbu Chelvan", ORANGE),
    ("S Roopesh", GREEN),
    ("B. Charith Reddy", SLATE),
    ("Y Rupesh Reddy", ROSE),
]

# One entry per slide: title, what to say, a simple example, terms, and one likely question.
SLIDES = [
    dict(
        title="Title slide",
        say=[
            "Good morning everyone. We are team <b>Cash guard</b>. I am Anbu Chelvan, and my teammates are Roopesh, Charith Reddy and Rupesh Reddy.",
            "This is our Project Review 3 for Machine Learning, 21CSC305P. Our topic is <b>grouping warehouse products with K-Means clustering</b>.",
            "We studied the solutions given in Unit 3 and selected K-Means for our problem. I will explain the problem and the basic terms. Roopesh will explain why we chose K-Means. Charith will show how it works on our data. Rupesh will show the result and conclude.",
        ],
        example="Think of a supermarket. Milk and bread are kept where everyone can reach them quickly. We want a warehouse to place its products in the same smart way.",
        terms=[("K-Means clustering", "A method that divides data into k groups of similar items."),
               ("Unit 3", "The part of our syllabus on clustering, mixtures of Gaussians, factor analysis and PCA.")],
        ask=("What is your project in one line?", "We group similar warehouse products with K-Means so that they can be placed smartly and workers walk less."),
    ),
    dict(
        title="Our problem statement",
        say=[
            "A warehouse stores thousands of different products. Each product type is called an <b>SKU</b>. If products are kept in random places, workers walk a long way to collect the items of each order.",
            "Our problem asks us to <b>partition</b>, that is divide, the SKUs into groups of similar products. We group them using four things. One, <b>pick frequency</b>: how often it is picked. Two, <b>seasonal demand</b>: how fast it sells in each season. Three, <b>physical size</b>: length, width, height and weight. Four, <b>handling needs</b>: fragile, heavy or needing special care.",
            "Once we have the groups, the manager can decide where to keep each group. The goal is better inventory placement and less travel time.",
        ],
        example="At home, the things we use every day are kept within reach, and the things we use once a year are kept on the top shelf. A warehouse has too many products to decide this by hand, so we let the data decide.",
        terms=[("SKU", "Stock Keeping Unit: one unique product type."),
               ("Partition", "Divide into groups so that each item is in exactly one group."),
               ("Order fulfilment", "Collecting the items of an order and sending it out."),
               ("Inventory placement", "Deciding where each product is stored.")],
        ask=("Why does placement matter?", "Walking between shelves is a big part of a picker's work. If fast items are near the packing area, every order takes less walking."),
    ),
    dict(
        title="Key terms in simple words",
        say=[
            "Before the solution, six simple terms. <b>SKU</b> is one unique product type. A 1 litre water bottle is one SKU and a 500 ml bottle is another SKU.",
            "<b>Pick frequency</b> is how many times a product is taken from the shelf. <b>Seasonal demand velocity</b> is how fast it sells in a season: umbrellas in the monsoon, sweaters in winter.",
            "<b>Clustering</b> means dividing data into groups where the items in a group are very similar. The <b>centroid</b> is the centre, or average point, of a cluster. <b>Unsupervised learning</b> means the data has no labels, so the algorithm finds the groups by itself.",
            "Now Roopesh will explain the solutions we reviewed.",
        ],
        example="Clustering is like sorting a basket of mixed fruits. Nobody gives us the names, but we still put apples with apples and oranges with oranges because they look alike.",
        terms=[("Feature", "A measurable property, such as size or pick frequency."),
               ("Label", "The correct answer given along with the data. We have none."),
               ("Cluster", "A group of similar data points."),
               ("Centroid", "The mean point of a cluster.")],
        ask=("Why is this unsupervised learning?", "Nobody has told us which SKU belongs to which group. There are no labels, so the algorithm must find the groups."),
    ),
    dict(
        title="Unit 3 solutions we reviewed",
        say=[
            "Thank you, Anbu. Unit 3 gives us four kinds of solutions.",
            "First, <b>K-Means clustering</b>. It splits the data into k groups, and each item joins the nearest centre. Second, <b>Mixtures of Gaussians</b> with the EM algorithm. This is soft clustering: each item gets a probability for every group.",
            "Third, <b>hierarchical clustering</b>. It builds a tree of clusters, called a dendrogram, by merging or splitting step by step. Fourth, <b>PCA and factor analysis</b>. These reduce many features to a few, but they do not make groups.",
            "We compared all four with our problem and selected K-Means.",
        ],
        example="Hard clustering says: this student is in section A. Soft clustering says: 70% section A and 30% section B. A product on a shelf needs the first kind of answer.",
        terms=[("Hard clustering", "Each item belongs to exactly one group."),
               ("Soft clustering", "Each item gets a probability for every group."),
               ("Dendrogram", "A tree diagram that shows how clusters join."),
               ("EM algorithm", "Expectation-Maximization: guess, improve, and repeat."),
               ("PCA", "Principal Component Analysis: fewer features, same information as far as possible.")],
        ask=("Which of these make groups?", "K-Means, mixtures of Gaussians and hierarchical clustering make groups. PCA and factor analysis only reduce the number of features."),
    ),
    dict(
        title="Our choice: K-Means clustering",
        say=[
            "Our selected solution is K-Means. <b>K-Means groups similar data points into k clusters without needing labelled data.</b> Here k is simply the number of groups we want.",
            "Why does it suit our project? Reason one: our problem statement says partition, and K-Means is a partitioning method. Reason two: every SKU gets exactly one group, just as a product is kept in one storage zone.",
            "Reason three: all four inputs can be written as numbers, so the algorithm can measure the distance between products. Reason four: it is simple and fast even for thousands of SKUs, and we can run it again every season.",
        ],
        example="If k is 3, K-Means makes 3 groups. It is like dividing a class into 3 teams so that students with similar marks are in the same team.",
        terms=[("k", "The number of clusters we ask for."),
               ("Partitioning method", "A method that divides data into separate groups."),
               ("Labelled data", "Data that already has the correct answer attached."),
               ("Distance", "A number that says how different two items are.")],
        ask=("What is the weakness of K-Means?", "We must choose k before starting, and the features must be numbers on a similar scale. We handle both: the elbow method for k, and scaling for the features."),
    ),
    dict(
        title="Why not the other solutions",
        say=[
            "You may ask why we did not choose the other methods.",
            "<b>Mixtures of Gaussians</b> give a probability for every group. But a product cannot be kept 60% in one zone and 40% in another. We need one clear zone.",
            "<b>Hierarchical clustering</b> compares every pair of items, so it becomes slow for thousands of SKUs. <b>PCA and factor analysis</b> do not create groups at all. They can only help before clustering.",
            "<b>K-Means</b> gives k clear groups with one centre each. That is exactly what we need. Now Charith will explain how K-Means works.",
        ],
        example="With 1,000 SKUs there are about 5 lakh pairs to compare (1,000 x 999 / 2 = 4,99,500). K-Means only compares each SKU with the k centres, for example 1,000 x 4 = 4,000 distances in one round.",
        terms=[("Probability", "A number from 0 to 1 that says how likely something is."),
               ("Pair-wise comparison", "Checking every item against every other item."),
               ("Feature reduction", "Replacing many features with a few."),
               ("Zone", "One storage area of the warehouse.")],
        ask=("Can PCA still be used?", "Yes, as a first step. If we had very many features, PCA could reduce them, and then K-Means would make the groups."),
    ),
    dict(
        title="How K-Means works",
        say=[
            "Thank you, Roopesh. K-Means works in five steps.",
            "Step one: choose k centroids at random. Step two: measure the distance from each SKU to every centroid. Step three: assign each SKU to the nearest centroid.",
            "Step four: move each centroid to the mean, that is the average, of the SKUs in its cluster. Step five: repeat steps two to four until no SKU changes its cluster.",
            "The distance we use is <b>Euclidean distance</b>, which is the straight-line distance between two points.",
        ],
        example="Three teachers stand in a playground. Every student walks to the nearest teacher. Then each teacher moves to the middle of their group. Students again walk to the nearest teacher. When nobody moves any more, the groups are final.",
        terms=[("Euclidean distance", "Straight-line distance. For (1, 2) and (4, 6): square root of (3<super>2</super> + 4<super>2</super>) = 5."),
               ("Mean", "The average of the values."),
               ("Iteration", "One round of the repeated steps."),
               ("Convergence", "The point where nothing changes any more, so we stop.")],
        ask=("When does the algorithm stop?", "When no SKU moves to another cluster, or after a fixed number of rounds."),
    ),
    dict(
        title="Step 1: Prepare the SKU data",
        say=[
            "Now we apply K-Means to our problem. First we prepare the data. Each SKU becomes one row of numbers.",
            "In this example table, A101 is picked 120 times a week, its season index is 1.1, its volume is 2 litres and it is not fragile. These numbers are made up, only to show the idea.",
            "Handling needs are written as 0 or 1. Fragile is 1, not fragile is 0. <b>Season index</b> is peak-season sales divided by average sales. If it is 3.5, the product sells three and a half times more in its season.",
            "Finally we <b>scale</b> the features. Volume can be 180 while season index is only 1. Without scaling, the big number would control the distance.",
        ],
        example="Scaling is like converting marks out of 50 and marks out of 100 into percentages before comparing two students. After that, both subjects count equally.",
        terms=[("Vector", "A row of numbers that describes one item."),
               ("Season index", "Peak-season sales divided by average sales."),
               ("Flag", "A 0 or 1 value that means no or yes."),
               ("Scaling", "Bringing all features to the same range.")],
        ask=("What if a feature is not a number?", "We turn it into 0 / 1 flags. For example: fragile yes or no, heavy yes or no."),
    ),
    dict(
        title="Step 2: Choose the value of k",
        say=[
            "K-Means needs the value of k before it starts. We use the <b>elbow method</b> from Unit 3.",
            "We run K-Means for k equal to 1, 2, 3 and so on. Each time we note the error. The error is the within-cluster variance: how far the SKUs are from their own centroid. As k increases, the error decreases.",
            "We plot this as a curve. At one point the curve bends like an elbow. After that, more clusters help very little. That bend is the best k.",
            "In this example curve the bend is at k equal to 4, so we use 4 clusters. Now Rupesh will show the result.",
        ],
        example="A shop adds billing counters. Going from 1 counter to 4 makes the queue much shorter. Going from 4 to 8 helps only a little. The useful stopping point is 4. That is the elbow.",
        terms=[("Elbow method", "Pick the k where the error curve bends."),
               ("Within-cluster variance", "How spread out the items are inside their own cluster."),
               ("WCSS", "Within-Cluster Sum of Squares: the usual name for this error."),
               ("Optimal k", "The best number of clusters for the data.")],
        ask=("Is this curve from real data?", "No. It is an illustration of the method. With real SKU data we would plot the real values and read the bend."),
    ),
    dict(
        title="Step 3: Clusters become zones",
        say=[
            "Thank you, Charith. After K-Means runs, we get clusters of similar SKUs. In our example there are four.",
            "Cluster 1 is <b>fast movers</b>: picked very often and small. We keep them on front racks near packing. Cluster 2 is <b>seasonal</b> items: they sell fast in some months, so they go to a flexible zone and move forward in season.",
            "Cluster 3 is <b>bulky or heavy</b> items: kept at ground level near the loading dock. Cluster 4 is <b>special care</b>, such as fragile items: a separate protected area.",
            "The floor plan on the right shows this. Fast movers are closest to packing and dispatch. These are example clusters. The real clusters come from the data.",
        ],
        example="It is like a kitchen. Salt and oil are next to the stove. The big rice bag stays on the floor. Glass items are on a safe shelf. Festival vessels are kept at the back.",
        terms=[("Fast mover", "A product that is picked very often."),
               ("Slotting", "Deciding the storage place of each product."),
               ("Loading dock", "The place where trucks are loaded and unloaded."),
               ("Dispatch", "Sending the packed order out.")],
        ask=("Who decides the zone of each cluster?", "The manager. K-Means gives the groups, and the manager reads each group and gives it the right place."),
    ),
    dict(
        title="How this solves our problem",
        say=[
            "How does this solve our problem? Our goal was better placement and less travel time.",
            "First, <b>less walking</b>. Fast movers sit closest to packing, so pickers travel less for most orders. Second, <b>better placement</b>. Each zone holds products with similar size and handling needs.",
            "Third, <b>season ready</b>. When demand changes, we run K-Means again with new sales data and the zones update.",
            "How do we check the clusters? SKUs inside a cluster should look alike, which means low within-cluster variance. And each centroid should read like a typical product of that group.",
        ],
        example="Suppose the centroid of cluster 1 says: about 110 picks a week, small size, not fragile. We can read it as the typical fast small item, and the name of the cluster is clear.",
        terms=[("Travel time", "The time a worker spends walking to collect items."),
               ("Typical product", "What the centroid of a cluster describes."),
               ("Re-run", "Running the algorithm again with new data.")],
        ask=("How will you measure the improvement?", "By comparing the average walking distance per order before and after the new placement. We have not measured it yet; that is our next step."),
    ),
    dict(
        title="Conclusion",
        say=[
            "To conclude. Our problem was to group warehouse SKUs so that pickers travel less.",
            "From Unit 3 we selected <b>K-Means clustering</b>, because it is a simple partitioning method that gives every SKU one clear group.",
            "The outcome is a set of clear clusters that map directly to warehouse zones.",
            "Our next step is to test with real SKU data and compare different values of k. Thank you. We are happy to take your questions.",
        ],
        example="In one line: similar products together, fast products nearest, and the grouping done by data instead of by guesswork.",
        terms=[("Partitioning method", "A method that divides data into separate groups."),
               ("Outcome", "What the solution gives us in the end.")],
        ask=("If you had more time, what would you add?", "Real SKU data, a check of different k values with the elbow method, and a comparison of walking distance before and after."),
    ),
]

GLOSSARY = [
    ("Centroid", "The centre (mean point) of a cluster."),
    ("Cluster", "A group of similar data points."),
    ("Clustering", "Dividing data into groups of similar items."),
    ("Convergence", "When nothing changes any more and the algorithm stops."),
    ("Dendrogram", "A tree diagram from hierarchical clustering."),
    ("Elbow method", "Choosing k where the error curve bends."),
    ("EM algorithm", "Expectation-Maximization: guess, improve, repeat."),
    ("Euclidean distance", "Straight-line distance between two points."),
    ("Feature", "A measurable property of an item."),
    ("Hard clustering", "Each item is in exactly one group."),
    ("k", "The number of clusters we ask for."),
    ("Mixture of Gaussians", "Soft clustering with probabilities."),
    ("PCA", "Reduces many features to a few."),
    ("Pick frequency", "How often a product is picked."),
    ("Scaling", "Bringing features to the same range."),
    ("Season index", "Peak-season sales divided by average sales."),
    ("SKU", "Stock Keeping Unit: one product type."),
    ("Soft clustering", "Each item gets a probability per group."),
    ("Unsupervised learning", "Learning from data without labels."),
    ("Within-cluster variance", "How spread out items are inside a cluster."),
]

QUESTIONS = [
    ("Why K-Means and not mixtures of Gaussians?", "A product needs one fixed zone. K-Means gives one group per SKU; a mixture gives probabilities."),
    ("How did you choose k?", "With the elbow method: plot the error for many k values and pick the bend."),
    ("Which distance do you use?", "Euclidean distance, the straight-line distance, after scaling the features."),
    ("What are the limits of K-Means?", "k must be chosen first, features must be scaled numbers, and the result depends on the random start, so we run it more than once."),
    ("Are your numbers real?", "No. The table, the curve and the four clusters are examples that show the method. Real data is our next step."),
]


def box(flowables, bg, pad=8, width=CW):
    t = Table([[flowables]], colWidths=[width])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), pad + 2), ("RIGHTPADDING", (0, 0), (-1, -1), pad + 2),
        ("TOPPADDING", (0, 0), (-1, -1), pad), ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def band(speaker_no, name, color, slide_no):
    t = Table([[Paragraph(f"Speaker {speaker_no}: {name}", BAND),
                Paragraph(f"Slide {slide_no} of 12  |  about 1 minute", BAND_R)]],
              colWidths=[CW * 0.55, CW * 0.45])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def slide_page(i, s):
    speaker_no = i // 3 + 1
    name, color = SPEAKERS[speaker_no - 1]
    thumb_w = 252
    thumb = Image(str(HERE / f"thumb-{i + 1:02d}.jpg"), width=thumb_w, height=thumb_w * 9 / 16)
    terms = [Paragraph("TERMS TO KNOW", LABEL), Spacer(1, 3)]
    for term, meaning in s["terms"]:
        terms.append(Paragraph(f"<b>{term}:</b> {meaning}", TERM))
        terms.append(Spacer(1, 2.5))
    gap = 10
    top = Table([[thumb, box(terms, TINT, pad=7, width=CW - thumb_w - gap)]], colWidths=[thumb_w + gap, CW - thumb_w - gap])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    say = [Paragraph("SAY THIS", LABEL), Spacer(1, 4)]
    for para in s["say"]:
        say.append(Paragraph(para, SAY))
        say.append(Spacer(1, 7))
    q, a = s["ask"]
    return [
        band(speaker_no, name, color, i + 1), Spacer(1, 10),
        Paragraph(s["title"], H1), Spacer(1, 8),
        top, Spacer(1, 16),
        *say, Spacer(1, 8),
        box([Paragraph("SIMPLE EXAMPLE", LABEL), Spacer(1, 3), Paragraph(s["example"], BODY)], WARM), Spacer(1, 12),
        box([Paragraph("IF THE REVIEWER ASKS", LABEL), Spacer(1, 3),
             Paragraph(f"<b>Q: {q}</b>", BODY), Spacer(1, 2), Paragraph(f"A: {a}", BODY)], TINT),
        PageBreak(),
    ]


def cover():
    logo = Image(str(HERE / "srm-logo.png"), width=150, height=150 * 314 / 795)
    logo.hAlign = "LEFT"
    rows = [[Paragraph("Speaker", CELL_H), Paragraph("Slides", CELL_H), Paragraph("What they explain", CELL_H), Paragraph("Time", CELL_H)]]
    parts = ["Title, the problem statement, key terms", "Unit 3 solutions, our choice, why not the others",
             "How K-Means works, preparing the data, choosing k", "Clusters to zones, how it solves the problem, conclusion"]
    for n, ((name, _), part) in enumerate(zip(SPEAKERS, parts)):
        rows.append([Paragraph(f"{n + 1}. {name}", CELL_B), Paragraph(f"{n * 3 + 1} to {n * 3 + 3}", CELL),
                     Paragraph(part, CELL), Paragraph("about 3 min", CELL)])
    split = Table(rows, colWidths=[CW * 0.27, CW * 0.13, CW * 0.43, CW * 0.17])
    split.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, TINT]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, TINT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    tips = [
        "Each speaker has three slides and three pages in this script: one page per slide.",
        "The <b>Say this</b> part is written the way you can speak it. Say it in your own words; do not read it word for word.",
        "Use the <b>Simple example</b> if the idea is not clear, or if you have time.",
        "The last line of your third slide hands over to the next speaker by name.",
        "The whole presentation takes about 12 minutes. Keep to about one minute per slide.",
        "The table, the curve and the four clusters in the slides are examples. Say so if you are asked.",
    ]
    tip_flow = [Paragraph("HOW TO USE THIS SCRIPT", LABEL), Spacer(1, 4)]
    for t in tips:
        tip_flow.append(Paragraph(t, BODY, bulletText="•"))
        tip_flow.append(Spacer(1, 3))
    return [
        logo, Spacer(1, 26),
        Paragraph("21CSC305P  MACHINE LEARNING  |  PROJECT REVIEW 3", LABEL), Spacer(1, 6),
        Paragraph("Presentation Script", COVER_T), Spacer(1, 6),
        Paragraph("Grouping Warehouse Products with K-Means Clustering", COVER_S), Spacer(1, 4),
        Paragraph("Team Cash guard (No. 17)  |  13 October 2026  |  12 slides, 4 speakers, 3 slides each", SMALL),
        Spacer(1, 24),
        Paragraph("Who presents what", st("h2", fontName="Body-Bold", fontSize=14, leading=18, textColor=TEAL)), Spacer(1, 8),
        split, Spacer(1, 22),
        box(tip_flow, TINT, pad=10),
        PageBreak(),
    ]


def last_page():
    rows = []
    half = (len(GLOSSARY) + 1) // 2
    for a, b in zip(GLOSSARY[:half], GLOSSARY[half:] + [("", "")] * (half - len(GLOSSARY[half:]))):
        rows.append([Paragraph(f"<b>{a[0]}</b>", TERM), Paragraph(a[1], TERM),
                     Paragraph(f"<b>{b[0]}</b>", TERM), Paragraph(b[1], TERM)])
    g = Table(rows, colWidths=[CW * 0.17, CW * 0.33, CW * 0.17, CW * 0.33])
    g.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, TINT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))
    qa = []
    for q, a in QUESTIONS:
        qa.append(Paragraph(f"<b>Q: {q}</b>", BODY))
        qa.append(Paragraph(f"A: {a}", BODY))
        qa.append(Spacer(1, 6))
    return [
        Paragraph("All the terms in one place", H1), Spacer(1, 4),
        Paragraph("Every speaker should know these, whoever's slide the question comes on.", SMALL), Spacer(1, 8),
        g, Spacer(1, 16),
        Paragraph("Questions any speaker may get", H1), Spacer(1, 8),
        box(qa, WARM, pad=10),
    ]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Body", 8.5)
    canvas.setFillColor(SLATE)
    canvas.drawString(M, 9 * mm, "Team Cash guard  |  Project Review 3  |  Presentation script")
    canvas.drawRightString(W - M, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=M, rightMargin=M, topMargin=14 * mm, bottomMargin=16 * mm,
                      title="Presentation Script: Warehouse SKU Clustering with K-Means",
                      author="Team Cash guard", subject="Project Review 3, 21CSC305P Machine Learning")
frame = Frame(M, 16 * mm, CW, H - 30 * mm, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="page", frames=[frame], onPage=footer)])

story = cover()
for i, s in enumerate(SLIDES):
    story += slide_page(i, s)
story += last_page()
doc.build(story)
print("wrote", OUT)
