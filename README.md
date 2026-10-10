# Optimizer Analyzer MT5

Phân tích báo cáo tối ưu hoá của MetaTrader 5 (xuất ra XML) và đề xuất **range tham số ổn định**
cho lần tối ưu kế tiếp, thay vì chỉ chọn một bộ tham số "tốt nhất".

Với mỗi file XML, chương trình tạo ra report HTML tương tác (biểu đồ kèm nhận xét bằng
tiếng Việt), report văn bản đầy đủ và các file CSV.

---

## Bắt đầu nhanh

```bash
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt

python main.py                   # file XML mới nhất trong data/
python main.py data/a.xml data/b.xml
```

Mở file `output/<tên>_report.html` bằng trình duyệt (xem được khi offline).

### Ví dụ kết quả

Chạy trên [`data/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01.xml`](data/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01.xml)
(1,390 pass tối ưu):

| Output | File |
|---|---|
| Report HTML tương tác | [output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01_report.html](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01_report.html) |
| Report console đầy đủ | [output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/report.txt](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/report.txt) |
| Range khuyến nghị | [ranges.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/ranges.csv) |
| Các set Stable kèm cluster | [stable.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/stable.csv) |
| Tóm tắt cluster | [clusters.csv](output/AMFS_v2_XAU_M5_2026-08-10_fwd1-4_10-10_r01/clusters.csv) |

Kết luận của pipeline:

- 1,390 pass → 1,028 sau pre-filter số lệnh → 870 set Stable.
- Chọn 5/11 tham số để tối ưu (6 tham số còn lại cố định theo trung vị của cluster tốt nhất):
  `setSlowMAPeriod`, `setEntryScoreBuy`, `setEntryScoreSell`, `setLimitATR`, `setMaxPositions`.
- 2 cluster; cluster tốt nhất là cluster 1 (382 set, Forward trung vị 93.9, Back trung vị 84.5,
  consistency 0.85).

Range khuyến nghị cho lần tối ưu kế tiếp:

| Tham số | Từ | Đến | Center | Bước |
|---|---|---|---|---|
| setSlowMAPeriod | 108 | 276 | 198 | 12 |
| setEntryScoreBuy | 47 | 55 | 51 | 1 |
| setEntryScoreSell | 51 | 57 | 54 | 1 |
| setLimitATR | 0.5 | 1.5 | 1.0 | 0.5 |
| setMaxPositions | 1 | 1.5 | 1 | 1 |

Report HTML gồm các phần:

1. **Tóm tắt:** phễu từ số pass gốc đến khuyến nghị, kèm cảnh báo.
2. **Chọn bộ tham số:** bảng importance, mỗi tham số được ghi rõ *tối ưu* hay *cố định ở X* và lý do.
3. **Biểu đồ** (mỗi biểu đồ có "Cách đọc" và nhận xét theo dữ liệu):
   Forward vs Back, importance, bản đồ điểm 2 tham số, điểm theo từng tham số,
   Forward theo cluster, parallel coordinates.
4. **Cluster:** nhận xét từng cluster (khuyến nghị / lợi nhuận cao nhất / ổn định nhất /
   quá nhỏ / vùng xung quanh yếu).
5. **Range khuyến nghị:** nhận xét từng tham số, cảnh báo khi chạm biên vùng đã test.
6. **Các bộ tham số tốt nhất:** nhận xét từng set (Elite, overfit Back, điểm cô lập, ít lệnh, DD cao).

---

## Workflow

```
File XML
   |  loader             đọc SpreadsheetML (xử lý ô bị bỏ qua)
   v
features                 Gap, RelativeGap, Consistency, DDScore, Quality
   |  filtering          pre-filter: MIN_TRADES / MAX_EQUITY_DD
   v
importance               RandomForest trên toàn bộ dữ liệu (Forward, Consistency)
   |  selection          SELECT_MODE: cumulative | median | relative | top_n | all
   v
scoring                  FinalScore = tổng có trọng số, cắt outlier, min-max
   |  filtering          top N% theo điểm -> RelativeGap thấp  (+ danh sách elite)
   v
neighbourhood            vùng xung quanh tốt đến đâu, tính trên TOÀN BỘ lưới đã test
   |  clustering         KMeans, k chọn theo silhouette (k <= số dòng / MIN_AVG_CLUSTER)
   v
cluster_summary          xếp hạng cluster
   |  ranges / recommend range IQR, >= 1 bước lưới, cắt trong vùng đã test
   v
report.txt  report.html  ranges.csv  stable.csv  clusters.csv
```

### Các metric chính

| Metric | Định nghĩa |
|---|---|
| Gap / RelativeGap | `abs(Fwd - Back)`, và giá trị đó chia cho `max(abs(Fwd), abs(Back))` |
| Consistency | `min(abs(Fwd), abs(Back)) / max(...)`, bằng 1 khi hai kỳ giống hệt nhau |
| Quality | `Sharpe * ProfitFactor * Consistency` (công thức tạm thời) |
| FinalScore | tổng có trọng số của Forward, Back, PF, Sharpe, Consistency, Quality, điểm drawdown |
| Elite | `Forward > ELITE_MIN_FORWARD` và `Back > ELITE_MIN_BACK`; bỏ qua bộ lọc gap |
| NeighbourScore | FinalScore trung bình của các set đã test trong bán kính; điểm cô lập được 0 |

Mọi ngưỡng và trọng số nằm trong [optimizer_analyzer/config.py](optimizer_analyzer/config.py).
Tham số có giới hạn cứng (ví dụ `setMaxPositions >= 1`) khai báo trong `PARAM_BOUNDS`
để report không khuyên test vượt qua giới hạn đó.

---

## Cấu trúc dự án

```
main.py                 điểm vào
optimizer_analyzer/     package (xem Workflow)
  loader  features  importance  selection  scoring  filtering
  neighbourhood  clustering  cluster_summary  ranges  recommend
  report  commentary  plots  pipeline  config
data/                   file XML tối ưu hoá của MT5
output/                 <tên>_report.html + một thư mục cho mỗi lần run
scripts/                check_mt5_connection.py (cần MetaTrader5)
tests/                  smoke test
```

### Cấu trúc output

```
output/<tên>_report.html        mở file này
output/<tên>/report.txt         toàn bộ nội dung console
output/<tên>/ranges.csv         range khuyến nghị
output/<tên>/stable.csv         các set Stable kèm cluster và chỉ số vùng xung quanh
output/<tên>/clusters.csv       tóm tắt cluster
```

## Quy ước đặt tên file data

`<EA>_<SYMBOL>_<TF>_<ngày bắt đầu YYYY-MM-DD>_<fwd>_<kết thúc>_r<NN>.xml`, ví dụ
`AMFS_v2_XAU_M5_2026-08-03_fwd1-4_10-03_r01.xml`.

- Ngày kết thúc là `MM-DD` của năm bắt đầu, hoặc `YYYY-MM-DD` đầy đủ khi kỳ vắt qua nhiều năm.
- File chỉ có năm hoặc tháng thì dùng ngày đầu/cuối của kỳ đó.
- `unk` = chưa biết; `rNN` đánh số các lần chạy có cùng EA và kỳ.

## Giới hạn cần biết khi đọc kết quả

- **Forward và Back có thể dài khác nhau**, nên `Gap` và `Consistency` (số tuyệt đối) chỉ so sánh
  được khi hai kỳ gần bằng nhau. Xem tương quan Forward–Back trong report trước khi tin vào xếp hạng.
- **Ngưỡng Elite phụ thuộc từng file.** Nếu Elite chiếm gần hết Stable, report sẽ cảnh báo;
  khi đó nâng `ELITE_MIN_FORWARD/BACK`.
- **Range chạm biên vùng đã test** nghĩa là điểm tối ưu thật có thể nằm ngoài vùng đó;
  report sẽ cảnh báo, trừ khi biên đó là giới hạn trong `PARAM_BOUNDS`.
- Importance là impurity importance của RandomForest, không phải SHAP.

## Test

```bash
python -m pytest tests
```
