const { Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
        WidthType, ShadingType, AlignmentType, BorderStyle, ExternalHyperlink } = require('docx');
const fs = require('fs');

const W = 9360;                                   // 6.5" text column, DXA
const GREY = "EFEFEF", DARK = "D9D9D9";
const P = (t, o={}) => new Paragraph({ spacing:{after:120}, ...o,
  children: (Array.isArray(t)?t:[new TextRun(t)]) });
const B = s => new TextRun({ text:s, bold:true });
const H = (t, lvl=HeadingLevel.HEADING_1) =>
  new Paragraph({ text:t, heading:lvl, spacing:{before:280, after:140} });

function table(cols, head, rows, opts={}) {
  const cell = (t, o={}) => new TableCell({
    width:{size:o.w, type:WidthType.DXA},
    shading: o.sh ? {type:ShadingType.CLEAR, fill:o.sh, color:"auto"} : undefined,
    margins:{top:60,bottom:60,left:100,right:100},
    children:(Array.isArray(t)?t:[t]).map(x =>
      new Paragraph({ spacing:{after:0},
        children:[new TextRun({ text:String(x), bold:!!o.b, size:o.sz||19 })] })) });
  return new Table({
    width:{size:W, type:WidthType.DXA}, columnWidths:cols,
    rows:[ new TableRow({ tableHeader:true, children:
             head.map((h,i)=>cell(h,{w:cols[i], b:true, sh:DARK})) }),
      ...rows.map(r => new TableRow({ children:
         r.cells.map((c,i)=>cell(c,{w:cols[i], b:r.bold, sh:r.sh})) })) ]});
}

// ─────────────────────────────── the 28-meeting calendar
const CAL = [
 ["1","Wed Sep 2","L1 \u00b7 Course intro, the AI workflow, asset returns"],
 ["2","Wed Sep 9","L2 \u00b7 The panel and portfolio mathematics"],
 ["3","Mon Sep 14","L3 \u00b7 Sorts, breakpoints, long-short portfolios; WRDS"],
 ["4","Wed Sep 16","L4 \u00b7 Introduction to performance evaluation; factor models I"],
 ["5","Mon Sep 21","L5 \u00b7 Factor models II \u2014 where factors come from, the zoo"],
 ["6","Wed Sep 23","L6 \u00b7 Factor models III \u2014 multi-factor models, Fama-MacBeth"],
 ["7","Mon Sep 28","L7 \u00b7 Portfolio decomposition \u2014 top-down, bottom-up, characteristic"],
 ["8","Wed Sep 30","L8 \u00b7 Backtesting protocol"],
 ["9","Mon Oct 5","L9 \u00b7 Why should this work? \u2014 interpreting the evidence"],
 ["10","Wed Oct 7","Project pitches I \u2014 5 minutes per group"],
 ["\u2014","Mon Oct 12","Fall Break \u2014 no class"],
 ["11","Wed Oct 14","Review  (Legislative Day \u2014 Monday schedule)"],
 ["12","Mon Oct 19","MIDTERM \u2014 in class, 60 minutes"],
 ["13","Wed Oct 21","L10 \u00b7 Momentum and trend following"],
 ["14","Mon Oct 26","L11 \u00b7 Transaction costs"],
 ["15","Wed Oct 28","L12 \u00b7 Leverage, shorting, and the capital base"],
 ["16","Mon Nov 2","L13 \u00b7 Capital allocation I"],
 ["17","Wed Nov 4","L14 \u00b7 Capital allocation II \u2014 estimation error"],
 ["18","Mon Nov 9","Guest speaker"],
 ["19","Wed Nov 11","L15 \u00b7 Conditional strategies I \u2014 volatility timing"],
 ["20","Mon Nov 16","L16 \u00b7 Conditional strategies II \u2014 factor timing"],
 ["21","Wed Nov 18","Project pitches II \u2014 5 minutes per group"],
 ["22","Mon Nov 23","L17 \u00b7 Fundamental risk models (BARRA)"],
 ["23","Wed Nov 25","L18 \u00b7 PCA and statistical factors"],
 ["24","Mon Nov 30","L19 \u00b7 Machine learning"],
 ["\u2014","Wed Dec 2","No class"],
 ["25","Mon Dec 7","Final project presentations I"],
 ["26","Wed Dec 9","Final project presentations II"],
 ["27","Fri Dec 11","Final project presentations III"],
 ["28","Mon Dec 14","Review \u2014 cumulative"],
];

// ─────────────────────────────── the topic view
const TOPICS = [
 ["Portfolio construction","Python and pandas warm-up \u00b7 returns and excess returns \u00b7 the stacked panel \u00b7 portfolio weights \u00b7 sorts, breakpoints and long-short portfolios","1\u20133"],
 ["Expected returns I:\nfactor models","Performance evaluation: Sharpe, information and appraisal ratios \u00b7 where factors come from and the factor zoo \u00b7 multi-factor models and Fama-MacBeth \u00b7 decomposing a portfolio","4\u20137"],
 ["Expected returns II:\nevidence","Backtesting protocol \u00b7 why should this work? interpreting the evidence","8\u20139"],
 ["Pitches, review, midterm","Project pitches I \u00b7 review \u00b7 MIDTERM","10\u201312"],
 ["Momentum and\nimplementation","Momentum and trend following \u00b7 transaction costs \u00b7 leverage, shorting and the capital base","13\u201315"],
 ["Optimization","Capital allocation \u00b7 what estimation error does to it","16\u201317"],
 ["Conditional strategies","Guest speaker \u00b7 volatility timing \u00b7 factor timing \u00b7 project pitches II","18\u201321"],
 ["Risk models","Fundamental risk models (BARRA) \u00b7 PCA and statistical factors","22\u201323"],
 ["Machine learning","Many signals at once","24"],
 ["Final project","Presentations \u00b7 cumulative review","25\u201328"],
];

const doc = new Document({
 styles:{ default:{ document:{ run:{ font:"Calibri", size:22 } } } },
 sections:[{ properties:{ page:{ size:{width:12240, height:15840},
                                 margin:{top:1080,bottom:1080,left:1440,right:1440} } },
 children:[
  P([new TextRun({text:"New York University", size:22})], {alignment:AlignmentType.CENTER, spacing:{after:0}}),
  P([new TextRun({text:"Stern School of Business", size:22})], {alignment:AlignmentType.CENTER, spacing:{after:120}}),
  P([new TextRun({text:"Data-Driven Investing with Python and AI", bold:true, size:32})],
    {alignment:AlignmentType.CENTER, spacing:{after:0}}),
  P([new TextRun({text:"Fall 2026 (Tentative—Definitive only on first day of classes)", bold:true, size:26})],
    {alignment:AlignmentType.CENTER, spacing:{after:240},
     border:{bottom:{style:BorderStyle.SINGLE, size:6, color:"888888", space:8}}}),

  H("Instructor"),
  P("Professor: Alan Moreira", {spacing:{after:0}}),
  P("Office: KMC 9-62", {spacing:{after:0}}),
  P("Email: alan.moreira@nyu.edu", {spacing:{after:0}}),
  P("Office hours: see Brightspace"),

  H("Class Time"),
  P([new TextRun("The class meets in "), B("KMC 3-110"), new TextRun(" twice per week on "),
     B("Mondays and Wednesdays from 3:30PM – 4:45PM"), new TextRun(". The first class is on "),
     B("Wednesday, September 2"), new TextRun(". The last day of classes is "),
     B("Monday, December 14"), new TextRun(". There are 28 meetings.")]),
  P([new TextRun("We will "), B("not"), new TextRun(" have class on Monday, September 7 (Labor Day) or Monday, October 12 (Fall Break).")]),
  P([new TextRun("Two dates to note. "), B("Wednesday, October 14"),
     new TextRun(" is a Legislative Day and runs on a Monday schedule — we do meet. And "),
     B("Wednesday, November 25"),
     new TextRun(" is a regular class day for undergraduates; the Thanksgiving break falls on Thursday and Friday and does not affect us.")]),

  H("Content"),
  P("Welcome to a hands-on, data-driven deep dive into the world of investing! In this course, we’ll move beyond theory and bring investment concepts to life using real financial market data. Building on what you learned in Foundations of Finance, we’ll explore how markets move, how portfolios are built, and how to evaluate whether investment strategies perform—all through the lens of Python and AI."),
  P("What will you do in this course? A lot! You’ll learn how to:"),
  P("✅ Analyze security price movements"),
  P("✅ Build and estimate factor models (think CAPM, Fama-French, and beyond)"),
  P("✅ Construct optimized portfolios and alternative models of capital allocation"),
  P("✅ Evaluate investment strategies and assess real-world performance"),
  P("✅ Develop characteristic-based trading strategies like value and momentum investing"),
  P("✅ Manage real-world implementation challenges in large-scale portfolio management"),
  P("✅ Use machine learning techniques to discover new investment opportunities"),
  P("At its core, this course is about transforming you into a skilled empirical analyst who can confidently navigate large financial datasets. We will use AI heavily to write code — but most importantly, to understand how to check AI’s work. Code that runs is not code that is right, and the skill this course builds is catching the difference."),
  P([B("📌 Prerequisites: "), new TextRun("You must have completed Foundations of Finance. Previous exposure to Python is a must for you to take this class. Do you need to be a Python guru? Most problem sets will be submitted in Jupyter Notebook format, and Python will be our primary tool for analysis, but it is increasingly more important to understand what you want from the code than to write the code itself—the AI can do the code for you. For example, if you took Introduction to Programming for Data Science using Python you CERTAINLY know more than enough Python to complete this class successfully. In addition to Python and the content of Foundations, students need to be comfortable with basic statistics and basic algebra. Students are strongly encouraged to study the review handout on statistics at the beginning of the semester (Handout Statistics Review on the class website).")]),
  P("This course is all about the investment side of finance—so if you're more interested in corporate finance, this may not be the best fit, but the knowledge of how to work with data should be valuable more broadly. If you're excited about using data to uncover financial insights and want to develop the skills of a top-tier investment analyst, this course is for you. Get ready to code, analyze data, and invest."),

  H("Readings"),
  P("Since most of the topics studied in the class are not well covered in any single text, there is no required textbook for the class. Primary materials for the course are the lecture notes, plus readings for each class that will be regularly posted on Brightspace. Some of these readings will be required, others will be optional or background reading for interested students. Other class materials such as assignments, practice exams, course announcements and so on will also be posted on Brightspace."),
  P("The main class material is the Jupyter notebooks contained in the online class book. We also use PowerPoint slides when needed."),

  H("Class Website"),
  P("All the teaching material including slides, handouts and homework problems will be posted on NYU Brightspace. The class website also contains some finance links and articles."),

  H("Optional Reference Materials"),
  P("The books listed below are relevant for various aspects of the course, and at various points material from the books will be referred to in the lectures. Interested students who want to gain an in-depth understanding of particular aspects of the course should feel free to consult me about purchasing one or more of the texts below. None of them are required, however."),
  P([B("Textbooks and technical books")], {spacing:{after:40}}),
  P("Investments — Bodie, Kane and Marcus", {spacing:{after:0}}),
  P("Ang, Andrew. Asset Management: A Systematic Approach to Factor Investing. Oxford University Press, 2014.", {spacing:{after:0}}),
  P("Paleologo, Giuseppe A. The Elements of Quantitative Investing."),
  P([B("Popular / fun reading")], {spacing:{after:40}}),
  P("Trillions · The Man Who Solved the Market · The Big Short"),

  H("Software"),
  P("You should bring your laptop to class, charged. Thanks to Google Colab we can run all our data analysis directly from the browser, and it has Google’s AI built in as a chatbot."),
  P("Another option is Visual Studio Code, which has built-in Copilot support. Students can get Copilot for free through GitHub, but it is not a simple process. We do not have resources to support the management of a local Python installation on your machine, so I will not be able to help with libraries not working locally."),
  P([B("WRDS: "), new TextRun("you will need a WRDS account for one assignment later in the term. Start the signup in the first week — approval can take several days.")]),

  H("Staying Up-to-Date"),
  P("You are strongly encouraged to follow market news, broadly defined. See Brightspace for recommended sources. If you encounter an interesting article or podcast that you would like to share with the class, please feel free to email me."),

  H("Grading and Assignments"),
  P("The distribution of overall letter grades for the course will reflect Stern’s guidelines. Your final course grade will be based on the following:"),
  table([5600,3760], ["Component","Weight"], [
    {cells:["Assignments (eight, completion only)","20%"]},
    {cells:["Midterm","10% or 20%"]},
    {cells:["Final exam","25% or 35%"]},
    {cells:["Final project (group)","20%"]},
    {cells:["Class attendance, participation, and in-lecture challenges","15%"]},
  ]),
  P("", {spacing:{after:80}}),
  P("Note that there is some flexibility in the grading scheme, i.e. the balance between the midterm and final exam. Your midterm exam will be worth either 10% or 20% of your final course grade, depending on how well you do in the midterm relative to the final. I’ll correspondingly adjust the weight on the final exam (e.g. if your midterm weight is 20%, your final exam weight is 25%). I will do this adjustment automatically in a way that maximizes your overall grade. The intention here is to provide some insurance for you in case you “have a bad day” on the date of the midterm or the final exam."),

  P([B("Two kinds of work.")], {spacing:{after:40}}),
  P("There is a short challenge at the end of most lectures. Everyone works with the same data, so there is a right answer, and it is graded automatically — you will get your score and written feedback back before the next class. These challenges are started in class and finished at home. They are formative: they count toward participation, and their purpose is to tell you and me where you stand, not to rank you."),
  P("The assignments are different. Each one applies that block’s technique to your own group’s trading strategy, so there is no single right answer. They are graded on completion."),

  P([B("Assignments.")], {spacing:{after:40}}),
  P([new TextRun("Assignment 1 is a warm-up on shared data \u2014 Python, pandas, and the ways a spreadsheet misleads you. From Assignment 2 onward, each one applies that block\u2019s technique to your own group\u2019s strategy and a few additional topic relevant exercise. Note that you can always change your strategy through the class\u2014but you always need one.")]),
  P("There will be eight assignments plus a final project posted over the semester. Your overall assignment grade is based on completion only. You are encouraged to complete these assignments in a group of three students, but each student should submit their own copy. If you submit only 6 out of 8 you still get a perfect assignment score."),
  P([B("Every assignment is due on a Thursday, at midnight."), new TextRun(" One weekday, all term \u2014 you should never have to look it up. Due dates are listed in the course outline below and on Brightspace. You should assume that late submissions will not be counted, but Better Late than never\u2014so instead of asking me just submit late. If you ask me, I will tell you to go ahead and submit. Assignments should be submitted via Brightspace.")]),

  P([B("Final project.")], {spacing:{after:40}}),
  P("Each group develops one trading strategy across the whole term. Every assignment applies that week’s technique to your own strategy, so by December the project is largely built. You may change strategy during the course — each assignment is self-contained."),
  P("There are two pitch days, five minutes per group. The final report and code are due before the first day of presentations. Slides are due the morning of your presentation slot."),

  P("You should not expect a response to questions regarding assignment, midterm, and final material sent the night before the due date. If you would like to contest a midterm, final, or assignment grade, I will look at it within three days of you receiving back the material. I reserve the right to regrade the entire exam if you contest a grade."),

  P([B("Participation and attendance.")], {spacing:{after:40}}),
  P("Attendance is mandatory. Bringing your name card is mandatory as well. You are expected to arrive on time and not to leave the class unless absolutely necessary—please, no coffee runs in the middle of class. I expect you to engage during class by asking questions and bringing up relevant material—if you read a recent article please bring it up, or email me and I will bring it up during class. If you are shy or nervous about participating, that is a great way to start. I suggest you email me the article with two sentences explaining how it is relevant and we can discuss it in class."),

  P([B("Use of AI.")], {spacing:{after:40}}),
  P("Use AI, actively. Gemini in Colab, ChatGPT, Claude — this course is built around it. But if you submit work you cannot explain, that is a problem. I will cold-call you to walk through a decision: why this approach, what alternatives you considered, why you rejected them. A large part of what I am assessing is the explanation, not the code."),
 ]},

 // ── page 2+: the outline
 { properties:{ page:{ size:{width:12240, height:15840},
                       margin:{top:1080,bottom:1080,left:1440,right:1440} } },
   children:[
  H("Key dates"),
  P("Everything with a deadline, in one place. Assignments are due at midnight; anything marked \u201cin class\u201d happens during our normal meeting. Note exception Friday class on Dec 11."),
  table([2200,4900,2260], ["Date","What","Where"], [
    {cells:["Thu Sep 10","Assignment 1 due","Brightspace"]},
    {cells:["Thu Sep 17","Assignment 2 due","Brightspace"]},
    {cells:["Thu Sep 24","Assignment 3 due","Brightspace"]},
    {cells:["Wed Oct 7","Project pitches I \u2014 5 min per group","in class"], sh:"F2F2F2"},
    {cells:["Thu Oct 8","Assignment 4 due","Brightspace"]},
    {cells:["Mon Oct 19","MIDTERM \u2014 60 minutes","in class"], sh:"FFE0E0", bold:true},
    {cells:["Thu Oct 22","Assignment 5 due","Brightspace"]},
    {cells:["Thu Nov 5","Assignment 6 due","Brightspace"]},
    {cells:["Wed Nov 18","Project pitches II \u2014 5 min per group","in class"], sh:"F2F2F2"},
    {cells:["Thu Nov 19","Assignment 7 due","Brightspace"]},
    {cells:["Thu Dec 3","Assignment 8 due","Brightspace"]},
    {cells:["Sunday, Dec 6","Code and report due for all groups","Brightspace"], sh:"FFF2CC", bold:true},
    {cells:["Mon Dec 7","Final project presentations I \u2013 15 minutes per group","in class"], sh:"FFF2CC"},
    {cells:["Wed Dec 9","Final project presentations II","in class"], sh:"FFF2CC"},
    {cells:["Friday Dec 11","Final project presentations III","in class"], sh:"FFF2CC"},
    {cells:["Dec 16\u201322","FINAL EXAM \u2014 cumulative","exam period"], sh:"FFE0E0", bold:true},
  ]),
  P("", {spacing:{after:60}}),
  P([new TextRun({text:"Presentation slides are due the morning of your group\u2019s slot.", italics:true, size:19})]),
  P("", {spacing:{after:120}}),
  P([B("The midterm is Monday, October 19"),
     new TextRun(", in class, 60 minutes. You can bring a double sided A4 sheet cheat. It covers meetings 1\u20139 \u2014 everything we covered up to that date. The review session is the meeting before it, on Wednesday, October 14. Fall Break falls the week before, which is deliberate: it is the only light week of the term and it is there to be used as a study runway.")]),
  P([B("The final exam"), new TextRun(" is during the University final exam period, December 16\u201322. Do not book travel before knowing the date! 60 minutes. You can bring a double sided A4 sheet cheat. It is cumulative. Everything we covered is fair game. You may not bring a computer, tablet or phone.")]),
  P("", {spacing:{after:200}}),

  H("Course Outline \u2014 by topic"),
  P("The short version. The precise meeting-by-meeting schedule follows; every deadline is in the key-dates table above."),
  table([2600,5760,1000], ["Block","Topics","Meetings"], TOPICS.map(t=>({cells:t}))),

  P("", {pageBreakBefore:true, spacing:{after:0}}),
  H("Tentative Course Outline \u2014 by meeting"),
  P("The precise version. I reserve the right to adjust the readings throughout the term. Changes will not show up here but on Brightspace under announcements. I promise on net not to increase the reading load relative to what we currently have."),
  table([700,1600,7060], ["#","Date","Session"],
    CAL.map(r=>({cells:r,
      sh: r[2].startsWith("MIDTERM") ? "FFE0E0"
        : (/no class/i.test(r[2]) ? GREY
        : (/pitch|presentation|Review|Guest/i.test(r[2]) ? "F2F2F2" : undefined)),
      bold: r[2].startsWith("MIDTERM")}))),
 ]},

 // ── policies
 { properties:{ page:{ size:{width:12240, height:15840},
                       margin:{top:1080,bottom:1080,left:1440,right:1440} } },
   children:[
  H("Academic Integrity"),
  P("Our undergraduate Academics Pillar states that we take pride in our well-rounded education and approach our academics with honesty and integrity. Indeed, integrity is critical to all that we do here at NYU Stern. As members of our community, all students agree to abide by the NYU Stern Student Code of Conduct, which includes a commitment to:"),
  P("Exercise integrity in all aspects of one's academic work including, but not limited to, the preparation and completion of exams, papers and all other course requirements by not engaging in any method or means that provides an unfair advantage."),
  P("Clearly acknowledge the work and efforts of others when submitting written work as one’s own. Ideas, data, direct quotations (which should be designated with quotation marks), paraphrasing, creative expression, or any other incorporation of the work of others should be fully referenced."),
  P("Refrain from behaving in ways that knowingly support, assist, or in any way attempt to enable another person to engage in any violation of the Code of Conduct. Our support also includes reporting any observed violations of this Code of Conduct or other School and University policies that are deemed to adversely affect the NYU Stern community."),
  P("The Stern Code of Conduct and Judiciary Process applies to all students enrolled in Stern courses and can be found here: https://www.stern.nyu.edu/uc/codeofconduct."),
  P("To help ensure the integrity of our learning community, prose assignments you submit to Brightspace will be submitted to Turnitin. Turnitin will compare your submission to a database of prior submissions to Turnitin, current and archived web pages, periodicals, journals, and publications. Additionally, your document will become part of the Turnitin database."),

  H("General Conduct & Behavior"),
  P("Students are also expected to maintain and abide by the highest standards of professional conduct and behavior. Please familiarize yourself with Stern's Policy in Regard to In-Class Behavior & Expectations (http://www.stern.nyu.edu/portal-partners/current-students/undergraduate/resources-policies/academic-policies/index.htm) and the NYU Student Conduct Policy (https://www.nyu.edu/about/policies-guidelines-compliance/policies-and-guidelines/university-student-conduct-policy.html)."),

  H("Grading Guidelines"),
  P("At NYU Stern, we strive to create courses that challenge students intellectually and that meet the Stern standards of academic excellence. To ensure fairness and clarity of grading, the Stern faculty have agreed that for elective courses the individual instructor or department is responsible for determining reasonable grading guidelines. The Finance Department guidelines are that courses should generally have 35% of grades be A or A-."),

  H("Student Accessibility"),
  P("If you will require academic accommodation of any kind during this course, you must notify me at the beginning of the course and provide a letter from the Moses Center for Student Accessibility (212-998-4980, mosescsa@nyu.edu) verifying your registration and outlining the accommodations they recommend. If you will need to take an exam at the Moses Center for Student Accessibility, you must submit a completed Exam Accommodations Form to them at least one week prior to the scheduled exam time to be guaranteed accommodation. For more information, visit the CSA website: https://www.nyu.edu/students/communities-and-groups/student-accessibility.html"),

  H("Student Wellness"),
  P("Our aim is for students to be as successful academically as they can, and to help them overcome any impediments to that. Bookmark the NYU Stern Well-being Resource Hub (https://www.stern.nyu.edu/wellbeing) for existing services at NYU and Stern covering a wide variety of topics including financial well-being, relationship well-being, mental well-being, and more. Any student who may be struggling and believes this may affect their performance in this course is urged to contact the Moses Center for Student Accessibility (see also the Student Accessibility section of this syllabus) at 212-998-4980 to discuss academic accommodations. If mental health assistance is needed, call NYU’s 24/7 Wellness Exchange hotline at 212-443-9999. Furthermore, please approach me if you feel comfortable doing so. This will enable me to provide relevant resources or referrals. There are also drop-in hours and appointments. Find out more at http://www.nyu.edu/students/health-and-wellness/counseling-services.html"),

  H("Name Pronunciation and Pronouns"),
  P("NYU Stern students now have the ability to include their pronouns and name pronunciation in Albert. I encourage you to share your name pronunciation and preferred pronouns this way. Please use the Pronouns & Name Pronunciation link for additional information."),

  H("Religious Observances and Other Unique Situations"),
  P("NYU Stern is committed to ensuring an equitable educational experience for all students regardless of identity or religious/cultural background. The observance of religious and cultural holidays and traditions, and the recognition of unique circumstances—such as serving as a caregiver—are important aspects of this commitment. Please review all class dates at the start of the semester and review all course requirements to identify any foreseeable conflicts with exams, course assignments, projects, or other items required for participation and attendance. Please contact me within the first two weeks of the semester to discuss any potential conflicts."),

  H("Social Media"),
  P("Under no circumstances are students allowed to take pictures or record videos in class. This can lead to a violation of FERPA. And you absolutely should not post any pictures or videos of class on social media."),
 ]}]});

Packer.toBuffer(doc).then(b => { fs.writeFileSync("UG54_syllabus_fall2026.docx", b);
  console.log("✅ UG54_syllabus_fall2026.docx", b.length, "bytes"); });
