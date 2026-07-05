#!/usr/bin/env python3
"""Generate the analysis figures and assemble the PDF report into ~/Documents."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, HRFlowable)

OUT_DIR = os.path.expanduser('~/Documents')
FIG_DIR = os.path.dirname(os.path.abspath(__file__))
NAVY='#1b2a4a'; ACCENT='#b23a48'; GREY='#6b7280'

# ---------------- FIGURES ----------------
bins=list(range(-360,180,30))
xlbl=[b+15 for b in bins]
ALL=[0.345,0.324,0.351,0.459,0.446,0.345,0.318,0.432,0.378,0.291,0.372,0.324,0.318,0.291,0.331,0.439,0.486,0.351]
PUB=[1.028,0.972,1.083,1.361,1.306,1.111,0.722,1.139,0.944,0.722,0.750,0.556,0.806,0.528,0.861,1.139,1.333,0.750]
MEGA=[1.647,1.294,1.529,1.647,2.118,1.882,0.941,1.647,1.000,1.059,0.706,0.706,1.118,0.765,0.941,1.529,1.529,0.882]

# Fig 1 — event study
fig,ax=plt.subplots(figsize=(7.2,3.6))
ax.axvspan(-300,-120,color=ACCENT,alpha=0.08)
ax.axvline(0,color=GREY,ls='--',lw=1)
ax.plot(xlbl,ALL,'-o',ms=3,color=NAVY,label='All deals (N=148)')
ax.plot(xlbl,PUB,'-s',ms=3,color=ACCENT,label='Public ≥ $1B (N=36)')
ax.plot(xlbl,MEGA,'-^',ms=3,color='#2a7f62',label='≥ $10B mega (N=17)')
ax.text(-210,2.15,'"hump"\n~8 mo pre',ha='center',fontsize=7,color=ACCENT)
ax.text(6,2.05,'announce',rotation=90,fontsize=7,color=GREY,va='top')
ax.set_xlabel('days relative to announcement'); ax.set_ylabel('jet visits to target HQ\nper deal (30-day bin)')
ax.set_title('Event study: acquirer-jet visits around the deal announcement',fontsize=10,color=NAVY)
ax.legend(fontsize=7,frameon=False); ax.grid(alpha=0.2); fig.tight_layout()
fig.savefig(f'{FIG_DIR}/fig_eventstudy.png',dpi=160); plt.close(fig)

# Fig 2 — hump robustness collapse
fig,ax=plt.subplots(figsize=(7.2,3.2))
labels=['Raw\n(deal-pooled)','Activity-\nmatched','Drop top-2\ndeals','Drop top-5\ndeals','Deal-as-unit\n(binary)']
vals=[1.49,1.43,1.23,0.99,0.91]; sig=[True,True,False,False,False]
bars=ax.bar(labels,vals,color=[ACCENT if s else GREY for s in sig],alpha=0.85)
ax.axhline(1.0,color='k',lw=1); ax.set_ylabel('rate ratio (real / control)')
ax.set_title('The "hump" dissolves under robustness tests (all-deals)',fontsize=10,color=NAVY)
for b,v,s in zip(bars,vals,sig):
    ax.text(b.get_x()+b.get_width()/2,v+0.02,f'{v:.2f}'+('*' if s else ''),ha='center',fontsize=8)
ax.text(0.99,0.04,'* p<0.05    bars at/below 1.0 = no effect',transform=ax.transAxes,ha='right',fontsize=7,color=GREY)
ax.set_ylim(0,1.7); fig.tight_layout(); fig.savefig(f'{FIG_DIR}/fig_robustness.png',dpi=160); plt.close(fig)

# Fig 3 — critic positive control
fig,ax=plt.subplots(figsize=(7.2,3.2))
st=[0,0.5,1,2,3]; lr=[0.562,0.742,0.902,0.992,1.000]; mlp=[0.585,0.719,0.895,0.986,0.993]
ax.plot(st,lr,'-o',color=NAVY,label='Logistic'); ax.plot(st,mlp,'-s',color=ACCENT,label='Neural net')
ax.axhline(0.5,color=GREY,ls=':'); ax.scatter([0],[0.585],s=80,facecolor='none',edgecolor='k',zorder=5)
ax.annotate('real features only\n≈ 0.57 (weak, ~chance)',(0,0.585),(0.4,0.50),fontsize=7,
            arrowprops=dict(arrowstyle='->',color='k'))
ax.set_xlabel('strength of injected (known) signal, σ'); ax.set_ylabel('grouped-CV test AUC')
ax.set_title('Positive control: the pipeline recovers real signal when present',fontsize=10,color=NAVY)
ax.legend(fontsize=7,frameon=False); ax.grid(alpha=0.2); ax.set_ylim(0.45,1.03)
fig.tight_layout(); fig.savefig(f'{FIG_DIR}/fig_critic.png',dpi=160); plt.close(fig)

# ---------------- PDF ----------------
ss=getSampleStyleSheet()
H1=ParagraphStyle('H1',parent=ss['Heading1'],textColor=NAVY,fontSize=15,spaceBefore=10,spaceAfter=6)
H2=ParagraphStyle('H2',parent=ss['Heading2'],textColor=ACCENT,fontSize=11.5,spaceBefore=8,spaceAfter=3)
BODY=ParagraphStyle('BODY',parent=ss['BodyText'],fontSize=9.3,leading=13,alignment=TA_JUSTIFY,spaceAfter=5)
BULL=ParagraphStyle('BULL',parent=BODY,leftIndent=12,bulletIndent=2,spaceAfter=2)
TITLE=ParagraphStyle('TITLE',parent=ss['Title'],textColor=NAVY,fontSize=20,leading=24)
SUB=ParagraphStyle('SUB',parent=ss['Normal'],textColor=GREY,fontSize=11,alignment=TA_CENTER)
CAP=ParagraphStyle('CAP',parent=ss['Normal'],textColor=GREY,fontSize=7.6,alignment=TA_CENTER,spaceBefore=2,spaceAfter=8)
KEY=ParagraphStyle('KEY',parent=BODY,backColor='#f3f4f6',borderColor=NAVY,borderWidth=0.5,
                   borderPadding=6,leftIndent=4,rightIndent=4,fontSize=9.3,spaceBefore=4,spaceAfter=8)

def P(t,s=BODY): return Paragraph(t,s)
def B(t): return Paragraph('• '+t,BULL)
def tbl(data,colw,head=True):
    t=Table(data,colWidths=colw)
    st=[('FONT',(0,0),(-1,-1),'Helvetica',8.2),('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#d1d5db')),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4)]
    if head:
        st+=[('BACKGROUND',(0,0),(-1,0),colors.HexColor(NAVY)),('TEXTCOLOR',(0,0),(-1,0),colors.white),
             ('FONT',(0,0),(-1,0),'Helvetica-Bold',8.2),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f3f4f6')])]
    t.setStyle(TableStyle(st)); return t

E=[]
E.append(P('Corporate-Jet Flight Patterns, Economic Context,<br/>and S&amp;P 500 M&amp;A Activity',TITLE))
E.append(Spacer(1,4))
E.append(P('A predictive and econometric analysis of dealmaker jets, 2018–2026',SUB))
E.append(Spacer(1,2)); E.append(P('Internal research report · 23 June 2026',SUB))
E.append(Spacer(1,10)); E.append(HRFlowable(width='100%',color=colors.HexColor(NAVY),thickness=1))

E.append(P('Executive Summary',H1))
E.append(P('<b>Question.</b> Can corporate-jet flight patterns and/or the macroeconomic environment predict '
           'mergers &amp; acquisitions — which companies get acquired and when — and does a neural network extract '
           'structure that classical statistics miss?',BODY))
E.append(P('<b>Data.</b> 148 fully jet-trackable S&amp;P 500 acquisitions (acquirer with a confirmed business jet and '
           'flight history, matched to a geocoded target headquarters), spanning 48 acquirers and ~204,000 reconstructed '
           'flights, 2018–2026; macro context from Federal Reserve (FRED) series (policy rate, 10-year yield, VIX, '
           'credit spread, equity index).',BODY))
E.append(P('<b>Headline result.</b> Across five independent analyses — a per-deal flight classifier, an event study of '
           'pre-deal visitation, an economic-context model, a combined model, and an adversarial audit — corporate-jet '
           'activity does <b>not</b> provide an exploitable pre-deal signal, the economic regime explains only the '
           '<i>timing</i> of deal waves (not individual deal structure), and a neural network adds no value over linear '
           'models. The findings independently reproduce the prior <i>predfkitweball</i> project’s null/stationarity '
           'verdict and qualify the Oxford (2018) jet-tracking M&amp;A study (§5).',KEY))
E.append(P('Key findings',H2))
E.append(B('<b>Per-deal prediction is at chance.</b> Classifying target vs. non-target locations from flight patterns '
           'yields ROC-AUC 0.50 under honest, firm-grouped cross-validation. A neural network ties or loses to logistic '
           'regression in every configuration tested.'))
E.append(B('<b>The pre-deal "hump" is not robust.</b> Acquirer jets visit target HQs ~1.5× baseline 4–10 months before '
           'announcement — significant in a naïve test (p=0.009) but it collapses to null once one removes ~5 outlier '
           'same-sector deals, votes one-per-firm (14/28, p=1.00), or measures it per-deal (0.91×).'))
E.append(B('<b>The economy drives deal <i>timing</i>, weakly.</b> Deal flow peaks under zero rates and rising equities '
           '(2021) and troughs at peak rates (2023), but the relationship is modest (R²≈0.17). Deal <i>structure</i> '
           '(size, public/private) is essentially unexplained by macro; deal breakage leans weakly toward stress regimes.'))
E.append(B('<b>Combining the two sources adds nothing.</b> Flight + macro features predict no better than either alone. '
           'The only separable structure is a <i>stationary</i> acquirer-to-target-region affinity — a standing '
           'relationship, not a time-localized tip-off.'))
E.append(B('<b>The null survives adversarial audit.</b> A positive control proves the pipeline recovers injected signal '
           '(AUC→1.0); the network has ample capacity (fits random labels) but real features do not generalize past a '
           'weak ~0.57 ceiling shared by every model family.'))
E.append(Spacer(1,4))
E.append(P('<b>Bottom line.</b> Corporate-jet movement reflects where acquirers already have relationships, not where '
           'they are about to strike. The macro environment shapes when M&amp;A clusters but not the anatomy of '
           'individual deals. A neural network cannot manufacture depth the data does not contain.',KEY))

E.append(PageBreak())
E.append(P('1.  Scope &amp; Data',H1))
E.append(P('The universe is S&amp;P 500 firms that made true acquisitions (self-deals and buybacks excluded) over '
           '2018–2026 and for which a corporate jet was identified and confirmed. Starting from 1,063 jet-firm deals, we '
           'retain the subset that is <i>fully trackable from the jet side</i>: the acquirer has at least one confirmed '
           'business jet with flight history, and the target’s headquarters is geocoded. This yields the analysis set of '
           '<b>148 deals across 48 acquirers</b> ($746B disclosed value).',BODY))
E.append(tbl([['Layer','Count','Notes'],
              ['Jet-firm deals (non-self, true acq.)','1,063','any size, 2018–2026'],
              ['… with geocoded target HQ','148','the trackable analysis set'],
              ['Distinct acquirers','48','Blackstone alone = 43 deals (29%)'],
              ['Reconstructed flights','~204,000','OpenSky, 2018–2026'],
              ['Pre-90d jet visit to target HQ','38 / 148 (26%)','the raw "anchoring" rate'],
              ['Macro series (FRED)','5','fed funds, 10y, VIX, BAA spread, S&P 500']],
             [7.2*cm,2.6*cm,6.4*cm]))
E.append(Spacer(1,3))
E.append(P('Concentration is the central statistical hazard: a single acquirer (Blackstone) supplies 29% of deals, and a '
           'handful of large same-sector deals dominate the flight counts. Every test below is therefore evaluated with '
           'firm-grouped splits and outlier-robust statistics.',BODY))

E.append(P('2.  Methods',H1))
E.append(P('<b>Prediction (where).</b> Each observation is a (firm, location, 90-day window) cell. Positives are the 148 '
           'deals (acquirer → target-HQ region, pre-announcement); negatives are sampled firm×target-city×date cells with '
           'no associated deal. Features are deliberately <i>symmetric</i> — flight-pattern, firm-activity and '
           'location-popularity variables only, never deal attributes — so the label cannot leak in. Models are split '
           '<b>grouped by firm</b> (no firm in both train and test) and size-stratified, 2/3 train · 1/3 test.',BODY))
E.append(P('<b>Event study (when).</b> Visits near the target HQ are aligned on announcement day and tested against a '
           '<i>placebo-date</i> matched control: same firm, same city, the date shifted to nearby non-deal periods. '
           'Robustness adds activity-matching, one-vote-per-firm, outlier removal and a per-deal binary.',BODY))
E.append(P('<b>Economic context.</b> Each deal is joined to the macro regime at announcement. Occurrence is modeled at '
           'the monthly level; structure (size, target type, completion) with per-deal neural nets paired to permutation '
           'importance for interpretability. <b>Audit.</b> A positive-control / capacity / cross-model battery tests '
           'whether any null is an artifact of a weak model rather than absent signal.',BODY))

E.append(P('3.  Results',H1))
E.append(P('3.1  Flight patterns do not predict deals',H2))
E.append(P('Under firm-grouped cross-validation the deal-vs-non-deal classifier sits at chance (ROC-AUC 0.50 ± 0.06). The '
           'model cannot even fit the training set under regularization, a random split scores no better than the grouped '
           'one (so there is not even firm identity to exploit), and the neural network underperforms logistic regression.',BODY))

E.append(P('3.2  The pre-deal "hump" and why it is not real',H2))
E.append(Image(f'{FIG_DIR}/fig_eventstudy.png',width=15.5*cm,height=7.75*cm))
E.append(P('Figure 1.  Acquirer-jet visits to the target HQ peak ~8 months before announcement and fade into the deal '
           'date — a "diligence hump", not a final-quarter spike. The effect is largest for big, public, same-sector deals.',CAP))
E.append(P('Against the placebo-date control the hump is significant in aggregate (1.48×, p=0.009; 2.0× for mega-deals). '
           'But it does not survive the project’s standard robustness battery:',BODY))
E.append(Image(f'{FIG_DIR}/fig_robustness.png',width=15.5*cm,height=6.9*cm))
E.append(P('Figure 2.  The aggregate 1.48× is entirely carried by ~5 same-sector deals (Exxon→Pioneer/Denbury, '
           'ConocoPhillips→Marathon Oil, J&amp;J→Intra-Cellular). Removing them, voting one-per-firm (14/28, p=1.00), or '
           'measuring per-deal (0.91×) all return null.',CAP))

E.append(P('3.3  Economic context shapes timing, not structure',H2))
E.append(tbl([['Outcome','Neural net','Linear/logistic','Verdict'],
              ['Deal occurrence (monthly)','—','R²=0.17','Modest, real (rates ↓ / equity ↑ → more deals)'],
              ['Deal size (log $)','R²=−0.21','R²=0.02','No macro signal'],
              ['Public target','AUC 0.48','AUC 0.59','Weak'],
              ['Deal withdrawn','AUC 0.55','AUC 0.54','Weak; stress-leaning']],
             [4.6*cm,2.7*cm,3.0*cm,5.9*cm]))
E.append(Spacer(1,3))
E.append(P('Deal volume tracks the regime — highest under the 2021 zero-rate equity boom, lowest at the 2023 rate peak — '
           'but only modestly. Individual deal size is unpredictable from macro; deal breakage leans weakly toward '
           'inverted-curve, high-volatility regimes.',BODY))

E.append(P('3.4  Combined model: no synergy',H2))
E.append(P('A single model with both flight and macro features predicts no better than the flight features alone. Macro is '
           'a time-only signal (identical for every location at a given date): it can nudge the base rate by era but cannot '
           'identify <i>which</i> location is the target. The only separable structure is a stationary cross-sectional '
           'affinity between acquirers and their targets’ metros — consistent with a standing relationship rather than an '
           'imminent-deal signal.',BODY))

E.append(P('3.5  Adversarial audit: the null is genuine',H2))
E.append(Image(f'{FIG_DIR}/fig_critic.png',width=15.5*cm,height=6.9*cm))
E.append(P('Figure 3.  Injecting a known signal of increasing strength, the grouped-CV pipeline recovers it monotonically '
           'to AUC 1.0 — so "chance on real data" is trustworthy. The network has the capacity to fit random labels; real '
           'features simply do not generalize beyond a weak ~0.57 ceiling shared by logistic regression, random forests '
           'and k-NN alike. The result is not model-specific.',CAP))

E.append(P('4.  Cross-reference: independent replication of the predfkitweball null',H1))
E.append(tbl([['Test','predfkitweball (133 firms)','nwejets (148 deals)'],
              ['Raw within-pair / hump','1.50× (p=8e-4)','1.49× (p=0.010)'],
              ['Activity-matched','1.13× — NULL','1.43× (outlier-driven)'],
              ['Firm one-vote sign test','NULL everywhere','14/28, p=1.00 — NULL'],
              ['Remove outlier units','top-2 firms = 32% of hits','drop 5 deals → 0.99×'],
              ['Deal-as-unit','p overstated ~8×','35% < 38% — NULL'],
              ['Temporal shape','flat run-up, stationary','run-up/post ≈ baseline']],
             [4.8*cm,5.9*cm,5.5*cm]))
E.append(Spacer(1,3))
E.append(P('Two independent cohorts and pipelines both produce a raw ~1.5× effect that dissolves under the same controls. '
           'That convergence is itself the strong result: the honest finding is a constant, slightly elevated '
           'cross-sectional travel affinity between acquirers and their targets’ regions (industry/relationship '
           'proximity) — <b>not</b> an accelerating, predictable pre-deal jet signal, and no tradeable alpha.',KEY))

E.append(P('5.  Comparison to prior work: the Oxford study (2018)',H1))
E.append(P('The closest prior work is Strohmeier, Smith, Lenders &amp; Martinovic, <i>"The Real First Class? Inferring '
           'Confidential Corporate Mergers and Government Relations from Air Traffic Communication"</i> (IEEE European '
           'Symposium on Security &amp; Privacy, 2018). It is framed as a <b>privacy proof-of-concept</b> — not a '
           'predictive or trading study. Tracking 36 US/EU listed corporations over ~18 months of ADS-B data, the authors '
           'identified 7 M&amp;A cases in which the buyer’s aircraft visited the target before announcement — last visit on '
           'average 61 days prior, with month-before visits averaging 3 for cases versus 0.4 for a 31-firm non-acquirer '
           'control group. They explicitly cautioned that "false positives are always possible" and described the method as '
           'a "feeder or alert", not a primary source.',BODY))
E.append(tbl([['Dimension','Oxford 2018','This work (nwejets + predfkitweball)'],
              ['Goal','Privacy feasibility ("can you spot it?")','Prediction &amp; robustness ("can you forecast it?")'],
              ['Sample','36 firms, 7 selected cases, ~18 mo','148 deals / 48 firms (predf.: 133 firms, 1.2M flights)'],
              ['Control','31 other (non-acquirer) firms — cross-sectional','within-firm placebo-date + activity-matched + firm-one-vote'],
              ['Raw finding','cases 3 vs control 0.4 visits/mo; 61-day avg lead','raw hump 1.48× (p=0.009) — same raw phenomenon'],
              ['Under strong controls','not tested','collapses to null (firm-vote 14/28; drop 5 deals → 0.99×)'],
              ['Out-of-sample','none','grouped-CV AUC ≈ 0.50 (chance)'],
              ['Framing','"feeder/alert, not prime source"','null / stationary affinity; not tradeable']],
             [3.4*cm,5.5*cm,7.3*cm]))
E.append(Spacer(1,3))
E.append(P('The two studies are <b>consistent at the level of raw observation and differ only in the strength of claim.</b> '
           'Oxford’s elevation is a <i>cross-firm</i> comparison (acquirers vs. unrelated firms) — which our cross-sectional '
           'model reproduces (AUC ≈ 0.62). But under <i>within-firm, time-matched</i> controls, which a predictive claim '
           'requires, the signal falls to chance (AUC ≈ 0.50). Their 7 cases are the analogue of our ~5 outlier same-sector '
           'deals: across the full population only 26% of deals show any pre-90-day visit, and the aggregate effect '
           'disappears once one votes one-per-firm or removes the outliers. Even Oxford’s 61-day average is skewed by a '
           'single 325-day case. Notably, their own suggested fix — filtering by acquirer "viability" (industry, relative '
           'size) — is precisely the matched-control idea that, applied rigorously, removes the signal.',BODY))
E.append(P('We therefore do not refute the Oxford privacy proof-of-concept; we supply the predictive-grade stress test it '
           'left open. The answer is that corporate-jet visitation is a real but <i>stationary</i> acquirer-to-target '
           'affinity — observable in selected cases, but not a reliable, generalizable M&amp;A predictor.',KEY))

E.append(P('6.  Limitations',H1))
for t in [
  '<b>Sample size and concentration.</b> 148 deals across 48 firms, with one firm at 29%; cross-validation error bars are '
  'wide (±0.03–0.06 AUC), so even the weak 0.57 ceiling sits only ~1.5σ from chance.',
  '<b>Flight coverage.</b> OpenSky coverage is partial and grows over time; ~18% of airports did not resolve to '
  'coordinates. Coverage growth was controlled in the event study (placebos drawn in the same era) and works against, '
  'not for, the observed effect.',
  '<b>Identification.</b> The trackable set is bounded by geocoded targets and confirmed jets; opaque-trustee fleets and '
  'private targets are under-represented, which is itself informative about where the method can and cannot see.',
  '<b>Scope of claim.</b> A null on this set means "no exploitable per-deal signal at this granularity," not "jets are '
  'never used for deals." The stationary affinity is real; it is simply not predictive.']:
    E.append(B(t))

E.append(P('7.  Conclusion',H1))
E.append(P('Corporate-jet flight patterns encode a standing relationship between acquirers and the regions where their '
           'targets sit, but they do not forecast individual acquisitions: per-deal prediction is at chance, the '
           'pre-announcement "hump" is an artifact of a few same-sector deals and firm clustering, and the signal is '
           'cross-sectional rather than temporal. The macroeconomic regime governs when M&amp;A clusters — modestly — but '
           'not the structure of individual deals. Fusing the two information sources yields no synergy, and a neural '
           'network never outperforms a linear baseline because the underlying relationships are weak and low-dimensional. '
           'These results, reached on an independent dataset, reproduce the predfkitweball verdict: a null / stationarity '
           'finding rather than a predictive or tradeable one. The contribution is a rigorously negative, '
           'adversarially-audited result — and a reusable pipeline for testing such claims honestly.',BODY))
E.append(Spacer(1,6)); E.append(HRFlowable(width='100%',color=colors.HexColor('#d1d5db'),thickness=0.5))
E.append(P('Reproducibility: scripts <font face="Courier">nn_build_dataset / nn_train / nn_event_study / nn_hump_test / '
           'nn_hump_robustness / economic_context / combine_model / critic_test.py</font> in <font face="Courier">~/Documents/nwejets</font>. '
           'Figures generated by <font face="Courier">make_report.py</font>.',ParagraphStyle('fin',parent=BODY,fontSize=7.6,textColor=GREY)))

path=os.path.join(OUT_DIR,'Jet-MA-Analysis-Report.pdf')
SimpleDocTemplate(path,pagesize=A4,leftMargin=2*cm,rightMargin=2*cm,topMargin=1.6*cm,bottomMargin=1.6*cm,
                  title='Corporate-Jet Flight Patterns and S&P 500 M&A').build(E)
print('WROTE',path)
