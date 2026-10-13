// Project Review 3: warehouse SKU clustering with K-Means. 12 slides.
const pptxgen = require("pptxgenjs");
const SKILL = process.env.PPTX_SKILL;
const { applyTheme } = require(SKILL + "/scripts/apply_theme.js");
const OUT = process.argv[2] || "deck.pptx";

const THEME = {
  name: "Warehouse Clusters",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "16212B", lt1: "FFFFFF", dk2: "0F4C5C", lt2: "EAF2F3",
    accent1: "0F4C5C", accent2: "F28C28", accent3: "2A9D8F", accent4: "E9C46A",
    accent5: "5F7180", accent6: "D1495B", hlink: "0F4C5C", folHlink: "5F7180",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 in
pres.title = "Warehouse SKU Clustering with K-Means";
pres.subject = "Project Review 3, Machine Learning Unit 3";
pres.author = "Team Cash guard";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const S = pres.ShapeType;
const HEX = THEME.colors;

const FOOT = "Warehouse SKU clustering  |  Project Review 3";

// ---- layouts ---------------------------------------------------------------
const dot = (x, y, d, color) => ({ text: { text: "", options: { shape: S.ellipse, x, y, w: d, h: d, fill: { color }, line: { color } } } });

pres.defineSlideMaster({
  title: "TITLE_DARK",
  background: { color: C.text2 },
  objects: [
    // The institute's logo needs white behind it: its blue and grey vanish on the teal.
    { text: { text: "", options: { shape: S.roundRect, rectRadius: 0.08, x: 0.6, y: 0.4, w: 2.75, h: 1.12, fill: { color: C.background1 }, line: { color: C.background1, width: 0 } } } },
    { image: { path: __dirname + "/srm-logo.png", x: 0.75, y: 0.475, w: 2.45, h: 0.97, altText: "SRM Institute of Science and Technology logo" } },
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 1.8, w: 5.6, h: 1.75, fontSize: 34, bold: true, color: C.background1, align: "left", valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.6, y: 3.6, w: 5.6, h: 0.4, fontSize: 16, color: C.background2, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 8.0, h: 0.75, fontSize: 36, bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } },
    dot(8.72, 0.57, 0.2, C.accent2), dot(9.0, 0.57, 0.2, C.accent3), dot(9.28, 0.57, 0.2, C.accent4),
    { text: { text: FOOT, options: { x: 0.5, y: 5.17, w: 6, h: 0.3, fontSize: 10, color: C.accent5, align: "left", valign: "middle", margin: 0 } } },
  ],
  slideNumber: { x: 9.0, y: 5.17, w: 0.5, h: 0.3, fontSize: 10, color: C.accent5, align: "right" },
});

pres.defineSlideMaster({
  title: "CLOSING_DARK",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.45, w: 5.6, h: 0.8, fontSize: 36, bold: true, color: C.background1, align: "left", valign: "middle", margin: 0 }, text: "" } },
  ],
  slideNumber: { x: 9.0, y: 5.17, w: 0.5, h: 0.3, fontSize: 10, color: C.background2, align: "right" },
});

// ---- helpers ---------------------------------------------------------------
let n = 0;
const name = (what) => `${what} ${++n}`;
const card = (slide, x, y, w, h, color = C.background2, extra = {}) =>
  slide.addShape(S.roundRect, { x, y, w, h, fill: { color, ...(extra.transparency != null ? { transparency: extra.transparency } : {}) }, line: { color, width: 0, ...(extra.transparency != null ? { transparency: 100 } : {}) }, rectRadius: 0.08, objectName: name("Card") });
const text = (slide, t, o) => slide.addText(t, { isTextBox: true, margin: 0, valign: "top", align: "left", color: C.text1, fontSize: 14, objectName: name("Text"), ...o });
const badge = (slide, label, x, y, d, fill = C.accent2, color = C.background1, fontSize = 16) =>
  slide.addText(String(label), { shape: S.ellipse, x, y, w: d, h: d, fill: { color: fill }, line: { color: fill, width: 0 }, color, bold: true, fontSize, align: "center", valign: "middle", margin: 0, objectName: name("Badge") });
const content = (section, title, notes) => {
  const slide = pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
  slide.addText(title, { placeholder: "title" });
  slide.addNotes(notes);
  return slide;
};
// A little cluster of dots around a centre, the deck's motif.
const cluster = (slide, cx, cy, color, d = 0.2, ring = C.background1, k = 1) => {
  const off = [[-0.42, -0.2], [-0.12, -0.45], [0.3, -0.33], [0.46, 0.05], [0.18, 0.38], [-0.25, 0.3], [-0.5, 0.12]];
  for (const [dx, dy] of off) {
    slide.addShape(S.ellipse, { x: cx + dx * k - d / 2, y: cy + dy * k - d / 2, w: d, h: d, fill: { color }, line: { color, width: 0 }, objectName: name("Dot") });
  }
  const r = 0.26 * Math.max(k, 0.7);
  slide.addShape(S.ellipse, { x: cx - r / 2, y: cy - r / 2, w: r, h: r, fill: { color: ring }, line: { color, width: 2.5 * Math.max(k, 0.7) }, objectName: name("Centroid") });
};

// ---- 1. Title --------------------------------------------------------------
pres.addSection({ title: "Problem" });
{
  const s = pres.addSlide({ masterName: "TITLE_DARK", sectionTitle: "Problem" });
  s.addText("Grouping Warehouse Products with K-Means Clustering", { placeholder: "title" });
  s.addText("Project Review 3  |  Unit 3", { placeholder: "body" });
  text(s, [
    { text: "21CSC305P", options: { bold: true, color: C.accent4, fontSize: 18, breakLine: true } },
    { text: "MACHINE LEARNING", options: { bold: true, color: C.background1, fontSize: 18 } },
  ], { x: 3.6, y: 0.4, w: 2.6, h: 1.12, valign: "middle" });
  text(s, [
    { text: "Team: Cash guard (No. 17)", options: { bold: true, color: C.accent4, fontSize: 15, breakLine: true } },
    { text: "V. Anbu Chelvan,  S Roopesh,  B. Charith Reddy,  Y Rupesh Reddy", options: { color: C.background1, fontSize: 14, breakLine: true } },
    { text: "13 October 2026", options: { color: C.background2, fontSize: 12 } },
  ], { x: 0.6, y: 4.12, w: 5.6, h: 1.0, paraSpaceAfter: 6 });
  cluster(s, 7.45, 1.55, C.accent2, 0.24, C.text2);
  cluster(s, 8.65, 2.85, C.accent4, 0.24, C.text2);
  cluster(s, 7.35, 4.0, C.accent3, 0.24, C.text2);
  s.addNotes("Introduce the team and the topic. We group warehouse products using K-Means clustering, the solution we picked from Unit 3.");
}

// ---- 2. Problem statement --------------------------------------------------
{
  const s = content("Problem", "Our problem statement",
    "Read the problem in simple words. A warehouse has thousands of products. If similar products are grouped, managers can decide where to keep each group, and workers walk less. We group using four things shown in the cards.");
  card(s, 0.5, 1.25, 9.0, 0.95);
  text(s, "Group warehouse products (SKUs) that behave alike, so managers can place them smartly and workers walk less while picking orders.",
    { x: 0.7, y: 1.25, w: 8.6, h: 0.95, fontSize: 17, valign: "middle" });
  text(s, "We group the SKUs using four things", { x: 0.5, y: 2.33, w: 9, h: 0.3, bold: true, color: C.text2, fontSize: 15 });
  const items = [
    ["Pick frequency", "How often it is picked for orders", C.accent2],
    ["Seasonal demand", "How fast it sells in each season", C.accent3],
    ["Physical size", "Length, width, height and weight", C.accent5],
    ["Handling needs", "Fragile, heavy or needs special care", C.accent6],
  ];
  items.forEach(([t, d, col], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 2.7, 2.1, 1.5);
    badge(s, i + 1, x + 0.15, 2.82, 0.38, col);
    text(s, t, { x: x + 0.15, y: 3.27, w: 1.85, h: 0.32, bold: true, fontSize: 15, color: C.text2 });
    text(s, d, { x: x + 0.15, y: 3.6, w: 1.85, h: 0.55 });
  });
  card(s, 0.5, 4.38, 9.0, 0.5, C.accent1);
  text(s, "Goal: better inventory placement and less travel time during order fulfilment",
    { x: 0.7, y: 4.38, w: 8.6, h: 0.5, bold: true, fontSize: 15, color: C.background1, valign: "middle" });
}

// ---- 3. Key terms ----------------------------------------------------------
{
  const s = content("Problem", "Key terms in simple words",
    "Explain each term in one line before going further. SKU is one product type. Pick frequency and seasonal demand describe how a product moves. Clustering, centroid and unsupervised learning are the machine learning words we use later.");
  const terms = [
    ["SKU", "Stock Keeping Unit: one unique product type stored in the warehouse.", C.accent2],
    ["Pick frequency", "How many times a product is taken from the shelf to fill orders.", C.accent2],
    ["Seasonal demand velocity", "How fast a product sells in a season. Example: umbrellas in the monsoon.", C.accent2],
    ["Clustering", "Dividing data into groups where items in a group are very similar.", C.accent3],
    ["Centroid", "The centre (mean point) of a cluster. Each cluster has one.", C.accent3],
    ["Unsupervised learning", "Learning from data that has no labels. The algorithm finds the groups itself.", C.accent3],
  ];
  terms.forEach(([t, d, col], i) => {
    const x = 0.5 + Math.floor(i / 3) * 4.6;
    const y = 1.3 + (i % 3) * 1.25;
    card(s, x, y, 4.4, 1.1);
    s.addShape(S.ellipse, { x: x + 0.18, y: y + 0.2, w: 0.18, h: 0.18, fill: { color: col }, line: { color: col, width: 0 }, objectName: name("Dot") });
    text(s, t, { x: x + 0.48, y: y + 0.1, w: 3.8, h: 0.36, bold: true, fontSize: 16, color: C.text2, valign: "middle" });
    text(s, d, { x: x + 0.18, y: y + 0.5, w: 4.05, h: 0.55 });
  });
}

// ---- 4. Solutions reviewed -------------------------------------------------
pres.addSection({ title: "Choosing the solution" });
{
  const s = content("Choosing the solution", "Unit 3 solutions we reviewed",
    "Unit 3 gives four families of solutions. K-Means and hierarchical clustering make groups. Mixtures of Gaussians make soft groups with probabilities. PCA and factor analysis only reduce the number of features. We compared all of them for our problem.");
  const sols = [
    ["Centroid-based", "K-Means clustering", "Splits data into k groups. Each item joins the nearest centre.", true],
    ["Distribution-based", "Mixtures of Gaussians (EM)", "Soft clustering. Each item gets a probability for every group.", false],
    ["Tree-based", "Hierarchical clustering", "Builds a tree of clusters by merging or splitting step by step.", false],
    ["Fewer features", "PCA and Factor analysis", "Reduces many features to a few. It does not make groups.", false],
  ];
  sols.forEach(([tag, t, d, chosen], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.3, 2.1, 3.2, chosen ? C.accent1 : C.background2);
    const fg = chosen ? C.background1 : C.text1;
    text(s, tag, { x: x + 0.15, y: 1.45, w: 1.8, h: 0.3, fontSize: 11, bold: true, color: chosen ? C.accent4 : C.accent5 });
    text(s, t, { x: x + 0.15, y: 1.78, w: 1.8, h: 0.7, bold: true, fontSize: 17, color: chosen ? C.background1 : C.text2 });
    text(s, d, { x: x + 0.15, y: 2.55, w: 1.8, h: 1.3, color: fg });
    if (chosen) {
      s.addText("Our choice", { shape: S.roundRect, rectRadius: 0.15, x: x + 0.15, y: 3.95, w: 1.3, h: 0.36, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, color: C.text1, bold: true, fontSize: 13, align: "center", valign: "middle", margin: 0, objectName: name("Pill") });
    }
  });
  text(s, "From the Unit 3 syllabus: K-means, mixtures of Gaussians, EM, factor analysis, PCA, hierarchical clustering",
    { x: 0.5, y: 4.62, w: 9, h: 0.3, fontSize: 11, color: C.accent5, valign: "middle" });
}

// ---- 5. Our choice ---------------------------------------------------------
{
  const s = content("Choosing the solution", "Our choice: K-Means clustering",
    "This is the solution we selected. Say the definition slowly. Then give the four reasons. The strongest reason: our problem says partition, and K-Means is a partitioning method where every item gets exactly one group.");
  card(s, 0.5, 1.3, 3.9, 3.5, C.accent1);
  text(s, "DEFINITION", { x: 0.75, y: 1.5, w: 3.4, h: 0.3, fontSize: 12, bold: true, color: C.accent4, charSpacing: 2 });
  text(s, "K-Means groups similar data points into k clusters without needing labelled data.",
    { x: 0.75, y: 1.85, w: 3.4, h: 1.25, fontSize: 18, bold: true, color: C.background1 });
  text(s, "k = the number of groups we want", { x: 0.75, y: 3.15, w: 3.4, h: 0.3, color: C.background2 });
  cluster(s, 1.4, 4.15, C.accent2, 0.13, C.accent1, 0.62);
  cluster(s, 2.45, 4.15, C.accent4, 0.13, C.accent1, 0.62);
  cluster(s, 3.5, 4.15, C.accent3, 0.13, C.accent1, 0.62);
  text(s, "Why it suits our project", { x: 4.7, y: 1.3, w: 4.8, h: 0.35, bold: true, fontSize: 17, color: C.text2 });
  const why = [
    "Our task says \"partition\". K-Means is a partitioning method.",
    "Every SKU gets exactly one group, just like one storage zone.",
    "All four inputs can be written as numbers, so distance works.",
    "Simple, fast for thousands of SKUs, easy to re-run each season.",
  ];
  why.forEach((w, i) => {
    const y = 1.82 + i * 0.75;
    badge(s, i + 1, 4.7, y + 0.04, 0.4);
    text(s, w, { x: 5.25, y, w: 4.25, h: 0.6, valign: "middle" });
  });
}

// ---- 6. Why not the others -------------------------------------------------
{
  const s = content("Choosing the solution", "Why not the other solutions",
    "The reviewer will ask why we did not pick the others. Mixtures of Gaussians give probabilities, but a product needs one fixed zone. Hierarchical clustering compares every pair, so it is slow for a big warehouse. PCA and factor analysis do not make groups at all.");
  const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
  const pick = (t) => ({ text: t, options: { bold: true, color: C.text2, fill: { color: C.background2 } } });
  s.addTable([
    [head("Method"), head("What it gives"), head("Fit for our problem")],
    ["Mixtures of Gaussians (EM)", "A probability for every group (soft)", "A product cannot sit 60% in one zone and 40% in another."],
    ["Hierarchical clustering", "A tree of clusters (dendrogram)", "Compares every pair of items, so it gets slow for thousands of SKUs."],
    ["PCA / Factor analysis", "Fewer features", "Does not create groups. It can only help before clustering."],
    [pick("K-Means clustering"), pick("k clear groups, one centre each"), pick("Fits our need: one clear group for every SKU.")],
  ], {
    x: 0.5, y: 1.3, w: 9.0, colW: [2.4, 2.6, 4.0], rowH: [0.45, 0.72, 0.72, 0.72, 0.72],
    fontSize: 14, color: C.text1, valign: "middle", margin: [0.04, 0.12, 0.04, 0.12],
    border: { type: "solid", pt: 0.75, color: HEX.lt2 }, objectName: "Comparison table",
  });
}

// ---- 7. How K-Means works --------------------------------------------------
pres.addSection({ title: "Applying K-Means" });
{
  const s = content("Applying K-Means", "How K-Means works",
    "These are the five steps from Unit 3. Start with k random centres. Measure the distance of every SKU to every centre. Assign each SKU to the nearest centre. Move each centre to the mean of its SKUs. Repeat until no SKU changes its cluster.");
  const steps = [
    ["Pick k centres", "Choose k centroids at random to start."],
    ["Measure distance", "Find the distance from each SKU to every centroid."],
    ["Assign", "Put each SKU in the cluster with the nearest centroid."],
    ["Update centres", "Move each centroid to the mean of its SKUs."],
    ["Repeat", "Do steps 2 to 4 again until no SKU changes its cluster."],
  ];
  steps.forEach(([t, d], i) => {
    const x = 0.5 + i * 1.84;
    if (i < steps.length - 1) {
      s.addShape(S.line, { x: x + 0.62, y: 1.6, w: 1.2, h: 0, line: { color: C.accent5, width: 1.5, endArrowType: "triangle" }, objectName: name("Arrow") });
    }
    badge(s, i + 1, x, 1.33, 0.55, i === 4 ? C.accent3 : C.accent2, C.background1, 20);
    text(s, t, { x, y: 2.05, w: 1.64, h: 0.55, bold: true, fontSize: 15, color: C.text2 });
    text(s, d, { x, y: 2.62, w: 1.64, h: 1.35 });
  });
  card(s, 0.5, 4.15, 9.0, 0.62);
  text(s, [
    { text: "Distance used: ", options: { bold: true, color: C.text2 } },
    { text: "Euclidean distance, the straight-line distance between two points." },
  ], { x: 0.7, y: 4.15, w: 8.6, h: 0.62, valign: "middle" });
}

// ---- 8. Prepare the data ---------------------------------------------------
{
  const s = content("Applying K-Means", "Step 1: Prepare the SKU data",
    "First we turn every SKU into a row of numbers. The table is made-up example data, only to show the idea. Handling needs become 0 or 1 flags. Then we scale the columns, because K-Means uses distance and a large number like volume would otherwise dominate.");
  text(s, "Example data (made up to show the idea)", { x: 0.5, y: 1.22, w: 5.3, h: 0.28, fontSize: 11, color: C.accent5, valign: "middle" });
  const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 }, align: "center" } });
  const num = (t) => ({ text: t, options: { align: "center" } });
  s.addTable([
    [head("SKU"), head("Picks / week"), head("Season index"), head("Volume (L)"), head("Fragile")],
    ["A101", num("120"), num("1.1"), num("2"), num("0")],
    ["B205", num("8"), num("3.5"), num("15"), num("0")],
    ["C310", num("15"), num("1.0"), num("180"), num("0")],
    ["D412", num("60"), num("1.2"), num("4"), num("1")],
  ], {
    x: 0.5, y: 1.55, w: 5.3, colW: [0.8, 1.15, 1.2, 1.15, 1.0], rowH: [0.62, 0.42, 0.42, 0.42, 0.42],
    fontSize: 14, color: C.text1, valign: "middle", margin: [0.03, 0.08, 0.03, 0.08],
    border: { type: "solid", pt: 0.75, color: HEX.lt2 }, objectName: "Example SKU table",
  });
  card(s, 0.5, 4.08, 5.3, 0.68);
  text(s, [
    { text: "Season index ", options: { bold: true, color: C.text2 } },
    { text: "= peak-season sales divided by average sales" },
  ], { x: 0.68, y: 4.08, w: 4.95, h: 0.68, valign: "middle" });
  const pts = [
    ["One row per SKU", "Each product becomes a row of numbers (a vector)."],
    ["Everything as numbers", "Handling needs become 0 / 1 flags such as fragile or heavy."],
    ["Scale the features", "Bring all columns to the same range so big numbers do not dominate."],
  ];
  pts.forEach(([t, d], i) => {
    const y = 1.3 + i * 1.17;
    badge(s, i + 1, 6.1, y, 0.4);
    text(s, t, { x: 6.62, y, w: 2.88, h: 0.34, bold: true, fontSize: 15, color: C.text2, valign: "middle" });
    text(s, d, { x: 6.62, y: y + 0.36, w: 2.88, h: 0.75 });
  });
}

// ---- 9. Choose k -----------------------------------------------------------
{
  const s = content("Applying K-Means", "Step 2: Choose the value of k",
    "K-Means needs k before it starts. We use the elbow method from Unit 3. Run K-Means for many values of k and plot the within-cluster variance. The curve falls fast and then flattens. The bend is the best k. The curve shown is an illustration, where the bend is at k equal to 4.");
  s.addChart(pres.charts.LINE, [{ name: "Within-cluster variance", labels: ["1", "2", "3", "4", "5", "6", "7", "8"], values: [100, 62, 38, 24, 20, 18, 16.5, 15.5] }], {
    x: 0.5, y: 1.3, w: 5.2, h: 3.55,
    showTitle: true, title: "Example elbow curve (illustrative)", titleFontSize: 12, titleColor: HEX.dk2, titleFontFace: "+mn-lt",
    chartColors: [HEX.accent2], lineSize: 3, lineDataSymbol: "circle", lineDataSymbolSize: 8,
    showLegend: false, showValue: false,
    showCatAxisTitle: true, catAxisTitle: "Number of clusters (k)", catAxisTitleFontSize: 11, catAxisTitleColor: HEX.accent5, catAxisTitleFontFace: "+mn-lt",
    showValAxisTitle: true, valAxisTitle: "Within-cluster variance", valAxisTitleFontSize: 11, valAxisTitleColor: HEX.accent5, valAxisTitleFontFace: "+mn-lt",
    catAxisLabelColor: HEX.accent5, valAxisLabelColor: HEX.accent5, catAxisLabelFontSize: 11, valAxisLabelFontSize: 11,
    catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt",
    valGridLine: { color: HEX.lt2, size: 0.75 }, catGridLine: { style: "none" }, valAxisMinVal: 0,
    objectName: "Elbow chart",
  });
  const pts = [
    ["Try many values", "Run K-Means for k = 1, 2, 3 and so on. Note the error each time."],
    ["Plot the curve", "Error = within-cluster variance. It falls as k grows."],
    ["Find the elbow", "Pick the k where the curve bends. More clusters after it help very little."],
  ];
  pts.forEach(([t, d], i) => {
    const y = 1.3 + i * 1.03;
    badge(s, i + 1, 6.0, y, 0.4);
    text(s, t, { x: 6.52, y, w: 2.98, h: 0.34, bold: true, fontSize: 15, color: C.text2, valign: "middle" });
    text(s, d, { x: 6.52, y: y + 0.36, w: 2.98, h: 0.62 });
  });
  s.addText("In this example: k = 4", { shape: S.roundRect, rectRadius: 0.15, x: 6.0, y: 4.42, w: 3.5, h: 0.43, fill: { color: C.accent2 }, line: { color: C.accent2, width: 0 }, color: C.text1, bold: true, fontSize: 15, align: "center", valign: "middle", margin: 0, objectName: name("Pill") });
}

// ---- 10. Clusters become zones ---------------------------------------------
{
  const s = content("Applying K-Means", "Step 3: Clusters become zones",
    "After K-Means runs, each cluster is a group of similar SKUs. The manager gives each cluster a zone. Fast movers go closest to packing. Seasonal items go to a flexible zone. Bulky items stay at ground level near the dock. Fragile items get a protected area. These four clusters are an example.");
  const head = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.accent1 } } });
  const b = (t) => ({ text: t, options: { bold: true, color: C.text2 } });
  s.addTable([
    [head("Cluster"), head("SKUs in it"), head("Where to place")],
    [b("1  Fast movers"), "Picked very often, small", "Front racks, near packing"],
    [b("2  Seasonal"), "Sell fast in some months", "Flexible zone, moved forward in season"],
    [b("3  Bulky / heavy"), "Large or heavy items", "Ground level, near loading dock"],
    [b("4  Special care"), "Fragile items", "Separate protected area"],
  ], {
    x: 0.5, y: 1.3, w: 5.6, colW: [1.65, 1.9, 2.05], rowH: [0.45, 0.68, 0.68, 0.68, 0.68],
    fontSize: 14, color: C.text1, valign: "middle", margin: [0.04, 0.1, 0.04, 0.1],
    border: { type: "solid", pt: 0.75, color: HEX.lt2 }, objectName: "Cluster to zone table",
  });
  text(s, "Example clusters. The real clusters come from the data.", { x: 0.5, y: 4.58, w: 5.6, h: 0.3, fontSize: 11, color: C.accent5, valign: "middle" });
  // Example floor plan
  card(s, 6.4, 1.3, 3.1, 3.55);
  text(s, "Example floor plan", { x: 6.55, y: 1.38, w: 1.6, h: 0.28, fontSize: 11, bold: true, color: C.text2, valign: "middle" });
  text(s, "Loading dock", { x: 8.0, y: 1.38, w: 1.35, h: 0.28, fontSize: 11, color: C.accent5, align: "right", valign: "middle" });
  const zones = [
    [6.55, 1.72, "2", "Seasonal", C.accent4, C.text1],
    [8.05, 1.72, "3", "Bulky / heavy", C.accent5, C.background1],
    [6.55, 2.92, "1", "Fast movers", C.accent2, C.text1],
    [8.05, 2.92, "4", "Special care", C.accent6, C.background1],
  ];
  zones.forEach(([x, y, num, label, fill, fg]) => {
    s.addText([
      { text: num, options: { fontSize: 22, bold: true, breakLine: true } },
      { text: label, options: { fontSize: 12, bold: true } },
    ], { shape: S.roundRect, rectRadius: 0.06, x, y, w: 1.3, h: 1.05, fill: { color: fill }, line: { color: fill, width: 0 }, color: fg, align: "center", valign: "middle", margin: 0.04, objectName: name("Zone") });
  });
  s.addText("Packing and dispatch", { shape: S.roundRect, rectRadius: 0.06, x: 6.55, y: 4.15, w: 2.8, h: 0.5, fill: { color: C.accent1 }, line: { color: C.accent1, width: 0 }, color: C.background1, bold: true, fontSize: 13, align: "center", valign: "middle", margin: 0, objectName: name("Packing") });
}

// ---- 11. How this solves the problem ---------------------------------------
pres.addSection({ title: "Conclusion" });
{
  const s = content("Conclusion", "How this solves our problem",
    "Link back to the problem statement. The goal was better placement and less travel time. Fast movers near packing means less walking. Similar products together means better placement. And when demand changes with the season, we simply run K-Means again.");
  const wins = [
    ["Less walking", "Fast movers sit closest to packing, so pickers travel less for most orders.", C.accent2],
    ["Better placement", "Each zone holds products with similar size and handling needs.", C.accent3],
    ["Season ready", "Re-run K-Means with new sales data and the zones update.", C.accent6],
  ];
  wins.forEach(([t, d, col], i) => {
    const x = 0.5 + i * 3.07;
    card(s, x, 1.3, 2.87, 2.4);
    badge(s, i + 1, x + 0.2, 1.48, 0.55, col, C.background1, 20);
    text(s, t, { x: x + 0.2, y: 2.15, w: 2.5, h: 0.38, bold: true, fontSize: 18, color: C.text2, valign: "middle" });
    text(s, d, { x: x + 0.2, y: 2.56, w: 2.5, h: 1.05 });
  });
  card(s, 0.5, 3.92, 9.0, 0.9);
  text(s, [
    { text: "How we check the clusters: ", options: { bold: true, color: C.text2 } },
    { text: "SKUs inside a cluster should look alike (low within-cluster variance), and each centroid should read like a typical product." },
  ], { x: 0.7, y: 3.92, w: 8.6, h: 0.9, valign: "middle" });
}

// ---- 12. Conclusion --------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "CLOSING_DARK", sectionTitle: "Conclusion" });
  s.addText("Conclusion", { placeholder: "title" });
  const lines = [
    "Problem: group warehouse SKUs so that pickers travel less.",
    "Chosen from Unit 3: K-Means clustering, a simple partitioning method.",
    "Outcome: clear clusters that map directly to warehouse zones.",
  ];
  lines.forEach((l, i) => {
    const y = 1.5 + i * 0.9;
    badge(s, i + 1, 0.6, y + 0.1, 0.42);
    text(s, l, { x: 1.2, y, w: 4.9, h: 0.62, fontSize: 16, color: C.background1, valign: "middle" });
  });
  text(s, "Next step: test with real SKU data and compare different values of k.", { x: 0.6, y: 4.3, w: 5.5, h: 0.5, color: C.background2, valign: "middle" });
  card(s, 6.5, 1.5, 3.0, 2.3, C.background1, { transparency: 88 });
  text(s, "Thank you", { x: 6.5, y: 2.05, w: 3.0, h: 0.6, fontSize: 32, bold: true, color: C.background1, align: "center", valign: "middle" });
  text(s, "Questions are welcome", { x: 6.5, y: 2.75, w: 3.0, h: 0.4, color: C.background2, align: "center", valign: "middle" });
  cluster(s, 7.1, 4.45, C.accent2, 0.13, C.text2, 0.62);
  cluster(s, 8.0, 4.45, C.accent4, 0.13, C.text2, 0.62);
  cluster(s, 8.9, 4.45, C.accent3, 0.13, C.text2, 0.62);
  s.addNotes("Close with the three points: the problem, the chosen solution and the outcome. Mention the next step, then invite questions.");
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("wrote", OUT);
})().catch((e) => { console.error("BUILD FAILED:", e.message); process.exit(1); });
