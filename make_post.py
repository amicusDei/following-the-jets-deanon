#!/usr/bin/env python3
"""Build a screenshot-ready one-page PDF of the LinkedIn post + a polished event-study
hump chart, into ~/Documents."""
import os
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                HRFlowable)
from reportlab.lib.utils import ImageReader

OUT=os.path.expanduser('~/Documents'); HERE=os.path.dirname(os.path.abspath(__file__))
NAVY='#16243f'; ACCENT='#b23a48'; GREEN='#2a7f62'; GREY='#5b6472'

# ---------- polished chart (general-audience labels) ----------
binstart=list(range(-360,180,30))
centers=[b+15 for b in binstart]
months=[c/30.44 for c in centers]
ALL=[0.345,0.324,0.351,0.459,0.446,0.345,0.318,0.432,0.378,0.291,0.372,0.324,0.318,0.291,0.331,0.439,0.486,0.351]
MEGA=[1.647,1.294,1.529,1.647,2.118,1.882,0.941,1.647,1.000,1.059,0.706,0.706,1.118,0.765,0.941,1.529,1.529,0.882]

plt.rcParams.update({'font.family':'DejaVu Sans','axes.edgecolor':'#9aa0aa','axes.linewidth':0.8})
fig,ax=plt.subplots(figsize=(8.6,4.0))
ax.axvspan(-9.9,-3.9,color=ACCENT,alpha=0.07,zorder=0)
ax.axvline(0,color=GREY,ls='--',lw=1.2,zorder=1)
ax.plot(months,MEGA,'-o',ms=4,lw=2.0,color=ACCENT,label='Mega-deals (≥ $10B)',zorder=3)
ax.plot(months,ALL,'-o',ms=4,lw=2.0,color=NAVY,label='All deals',zorder=3)
ax.annotate('apparent pre-deal "hump"\n≈ 8 months out',xy=(-7.9,2.12),xytext=(-11.2,2.35),
            fontsize=8.5,color=ACCENT,weight='bold',
            arrowprops=dict(arrowstyle='->',color=ACCENT,lw=1.1))
ax.text(0.18,2.05,'deal\nannounced',fontsize=8.5,color=GREY,va='top')
ax.set_xlabel('months relative to the public deal announcement',fontsize=10)
ax.set_ylabel('acquirer jet visits to the\ntarget HQ (per deal)',fontsize=10)
ax.set_title('Acquirers’ jets visit their targets, but mostly long before the deal',
             fontsize=11.5,color=NAVY,weight='bold',pad=10)
ax.set_xlim(-12.2,5.8); ax.set_ylim(0,2.55)
ax.legend(fontsize=9,frameon=False,loc='upper right')
ax.grid(axis='y',alpha=0.18)
for s in ['top','right']: ax.spines[s].set_visible(False)
fig.tight_layout()
CHART=f'{HERE}/fig_post_hump.png'; fig.savefig(CHART,dpi=220,bbox_inches='tight'); plt.close(fig)
CAL=f'{HERE}/fig_calibration.png'  # produced by make_calibration.py

# ---------- PDF (single tall card, screenshot-friendly) ----------
PW,PH=20.5*cm,42.3*cm
ss=getSampleStyleSheet()
EYE=ParagraphStyle('EY',parent=ss['Normal'],textColor=ACCENT,fontSize=9.5,leading=12,
                   alignment=TA_LEFT,fontName='Helvetica-Bold',spaceAfter=3)
TITLE=ParagraphStyle('T',parent=ss['Title'],textColor=NAVY,fontSize=19,leading=23,alignment=TA_LEFT)
BODY=ParagraphStyle('B',parent=ss['BodyText'],fontSize=10.3,leading=15,alignment=TA_JUSTIFY,spaceAfter=7,textColor='#1f2937')
CAP=ParagraphStyle('C',parent=ss['Normal'],fontSize=8.2,leading=11,textColor=GREY,alignment=TA_CENTER,spaceBefore=3,spaceAfter=2)
STAT=ParagraphStyle('ST',parent=ss['Normal'],fontSize=9.2,leading=13,textColor=NAVY,alignment=TA_CENTER)
DISC=ParagraphStyle('D',parent=ss['Normal'],fontSize=8.5,leading=11,textColor=GREY,alignment=TA_CENTER)

def P(t,s=BODY): return Paragraph(t,s)
E=[]
E.append(HRFlowable(width='100%',color=colors.HexColor(ACCENT),thickness=2.5,spaceAfter=8))
E.append(P('CORPORATE JET TRACKING',EYE))
E.append(P('Can you predict the next billion-dollar acquisition by following a CEO’s private jet?',TITLE))
E.append(Spacer(1,10))
E.append(P('This idea intrigued me, and then I found out someone had already studied it: <i>“The Real First Class? '
           'Inferring Confidential Corporate Mergers and Government Relations from Air Traffic Communication”</i> '
           '(Oxford &amp; armasuisse, 2018). So not a new approach, and one that has already made its way into the real '
           'world. My angle was a continuation with newer data and more aircraft.',BODY))
E.append(P('Using OpenSky I pulled <b>over 204,000 flights</b> and matched aircraft to <b>111 S&amp;P 500 companies</b>. '
           'The slow part was untangling the LLC and holding structures these jets hide behind. In the end I had '
           '<b>204 identified business jets</b> with geocoded headquarters and home airports, plus <b>148 M&amp;A deals '
           'over $500M</b> that I could fully track from the jet side. The first results looked promising:',BODY))
E.append(Image(CHART,width=16.6*cm,height=7.7*cm))
E.append(P('Aligning every deal on its announcement date, acquirer jets do visit the target’s HQ more around a deal, '
           'but the bump peaks ~8 months out and fades <i>into</i> the announcement, rather than spiking just before it.',CAP))
E.append(Spacer(1,4))
E.append(P('Then I ran proper statistical tests and landed exactly where the 2018 paper did, just with newer data: the '
           '“signal” is mostly a <i>standing</i> connection between acquirers and the regions their targets sit in, not a '
           'reliable pre-deal predictor. And it’s carried by a handful of deals, not a general pattern.',BODY))
E.append(P('Because the statistics were weak, I wanted a second opinion, so I tried several machine-learning approaches. '
           'None beat the baseline, and out-of-sample performance stayed close to random. I used a matched case-control '
           'sample, so the 25% base rate is by design, not the real takeover rate.',BODY))
if os.path.exists(CAL):
    _iw,_ih=ImageReader(CAL).getSize(); _cw=10.8*cm
    _img=Image(CAL,width=_cw,height=_cw*_ih/_iw); _img.hAlign='CENTER'
    E.append(Spacer(1,2)); E.append(_img)
    E.append(P('Out-of-sample calibration (firm-grouped CV). The 0.25 base rate is by construction, a case-control '
               'sample with 3 matched non-targets per target. If the model had skill the red curve would climb the '
               'diagonal; instead every point overlaps the base rate within its 95% CI, so the predictions carry no '
               'information.',CAP))
    E.append(Spacer(1,3))
E.append(P('Last, I checked whether the macro environment matters. A first pass suggests you can see the <i>waves</i> '
           'M&amp;A comes in (rates down, markets up, more deals), but not <i>which</i> firm will move. So it tracks the '
           'pro-cyclical risk appetite of the whole market, not a firm-specific signal.',BODY))
E.append(P('<b>Takeaway:</b> corporate-jet tracking is a fascinating dataset and a real privacy concern, but as an '
           'investing edge at population scale it’s closer to a gimmick than alpha. Where it can work is the opposite of '
           'a screen: you start with two firms you already suspect are talking, and the jet activity becomes one more '
           'piece of evidence.',BODY))
E.append(P('My most valuable result was the negative one. Being honest, it kind of broke my own expectations and gave me '
           'a reality check. The lesson was duller and more useful: check every step twice, because if it looks too good '
           'to be true, it usually is.',BODY))
E.append(Spacer(1,6))
E.append(HRFlowable(width='60%',color=colors.HexColor('#d1d5db'),thickness=0.6,spaceAfter=6))
E.append(P('204,024 flights · 204 business jets · 111 S&amp;P 500 firms · 148 trackable deals (&gt;$500M)',STAT))
E.append(Spacer(1,2))
E.append(P('Not financial advice! Just a student following his curiosity.',DISC))
E.append(Spacer(1,3))
E.append(P('Credits: OpenSky · the Oxford paper authors · WRDS for deal access',DISC))

path=os.path.join(OUT,'LinkedIn-Post-JetTracking.pdf')
SimpleDocTemplate(path,pagesize=(PW,PH),leftMargin=1.7*cm,rightMargin=1.7*cm,
                  topMargin=1.5*cm,bottomMargin=1.2*cm,title='Corporate Jet Tracking').build(E)
print('WROTE',path)
