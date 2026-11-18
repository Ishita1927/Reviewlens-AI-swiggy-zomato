import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

wb = openpyxl.Workbook()
ws = wb.active
ws.title = 'RICE'
A = Font(name='Arial')
B = Font(name='Arial', bold=True)
BLUE = Font(name='Arial', color='0000FF')
YEL = PatternFill('solid', fgColor='FFFF99')
HDR = PatternFill('solid', fgColor='D9E1F2')

def put(c, v, f=A, nf=None, fill=None):
    ws[c] = v
    ws[c].font = f
    if nf: ws[c].number_format = nf
    if fill: ws[c].fill = fill

put('A1', 'RICE scoring: Swiggy VoC project', Font(name='Arial', bold=True, size=14))
put('A4', 'Inputs from my data (600-review sample)', B)
put('A5', 'Reviews in sample');          put('B5', 600, BLUE)
put('A6', 'Reviews mentioning refund');  put('B6', 73, BLUE)
put('A7', 'Reviews mentioning support'); put('B7', 149, BLUE)
put('A8', 'Refund share of reviews');    put('B8', '=B6/B5', A, '0.0%')
put('A9', 'Support share of reviews');   put('B9', '=B7/B5', A, '0.0%')
put('A10', 'Users in scope per quarter (ASSUMPTION)'); put('B10', 1000000, BLUE, '#,##0', YEL)

heads = ['Scenario', 'Option', 'Share of users', 'Reach multiplier', 'Reach',
         'Impact', 'Confidence', 'Effort (person-months)', 'RICE score', 'Rank']
for i, h in enumerate(heads):
    c = ws.cell(12, i + 1, h)
    c.font = B
    c.fill = HDR
    c.alignment = Alignment(wrap_text=True)

opts = [('Refund status tracker', '$B$8'),
        ('Faster backend refunds', '$B$8'),
        ('More support staff', '$B$9')]
data = {'Low':  [(0.5, 0.5, 5), (1, 0.5, 12), (0.5, 0.5, 8)],
        'Base': [(1, 0.8, 3),   (2, 0.5, 9),  (1, 0.8, 6)],
        'High': [(2, 0.8, 2),   (3, 0.8, 6),  (2, 1.0, 4)]}
mult = {'Low': 0.5, 'Base': 1, 'High': 1.5}

r = 13
for sc in ['Low', 'Base', 'High']:
    start = r
    for (name, share), (imp, conf, eff) in zip(opts, data[sc]):
        put(f'A{r}', sc)
        put(f'B{r}', name)
        put(f'C{r}', f'={share}', A, '0.0%')
        put(f'D{r}', mult[sc], BLUE, '0.0')
        put(f'E{r}', f'=$B$10*C{r}*D{r}', A, '#,##0')
        put(f'F{r}', imp, BLUE)
        put(f'G{r}', conf, BLUE, '0%')
        put(f'H{r}', eff, BLUE)
        put(f'I{r}', f'=E{r}*F{r}*G{r}/H{r}', A, '#,##0')
        r += 1
    for k in range(start, r):
        put(f'J{k}', f'=RANK(I{k},$I${start}:$I${r-1})')
    r += 1

put(f'A{r}', 'Notes: impact, confidence, effort are my estimates. Shares come from % of reviews, not % of users.')
ws.column_dimensions['A'].width = 40
ws.column_dimensions['B'].width = 28
for col in 'CDEFGHIJ':
    ws.column_dimensions[col].width = 14

wb.save('docs/RICE_scoring.xlsx')
print('Saved docs/RICE_scoring.xlsx')