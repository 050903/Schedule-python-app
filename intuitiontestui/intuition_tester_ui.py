import random
import numpy as np
from sklearn.cluster import KMeans

# ==================== DỮ LIỆU BÀI TEST ====================
test_data = [
    {
        "question": "★ ▲ ★ ▲ ★ ?",
        "options": ["▲", "★", "●", "☂"],
        "pattern": 0
    },
    {
        "question": "● ● ▲ ● ● ?",
        "options": ["●", "▲", "★", "☂"],
        "pattern": 0
    },
    {
        "question": "▲ ★ ▲ ★ ▲ ?",
        "options": ["★", "▲", "☂", "●"],
        "pattern": 0
    },
    {
        "question": "☂ ☂ ● ☂ ☂ ?",
        "options": ["☂", "●", "▲", "★"],
        "pattern": 0
    },
    {
        "question": "★ ● ★ ● ★ ?",
        "options": ["●", "★", "▲", "☂"],
        "pattern": 0
    }
]

# ==================== AUTO RESPONSE VERSION ====================
def run_test_auto():
    print("=== Luyện Linh Tính - Phiên bản tự động ===")
    choices = []

    for i, q in enumerate(test_data):
        print(f"Câu {i + 1}: {q['question']}")
        for idx, opt in enumerate(q['options']):
            print(f"  {idx + 1}. {opt}")
        # Chọn ngẫu nhiên một đáp án (giả lập người dùng)
        ans = random.randint(0, 3)
        print(f"Chọn đáp án: {ans + 1} ({q['options'][ans]})")
        choices.append(ans)
        print("---------------------------\n")

    patterns = np.array([[q["pattern"]] for q in test_data])
    choices_np = np.array([[c] for c in choices])
    combined = np.concatenate((patterns, choices_np), axis=1)

    kmeans = KMeans(n_clusters=2, n_init='auto')
    kmeans.fit(combined)
    label = kmeans.labels_[-1]

    correct = sum(1 for i, q in enumerate(test_data) if q["pattern"] == choices[i])
    score = int((correct / len(test_data)) * 100)

    print("\n=== KẾT QUẢ ===")
    print(f"Điểm linh tính của bạn: {score}/100")
    print(f"Phân tích nhóm: {['Trực giác mạnh', 'Dựa vào ngẫu nhiên'][label]}")
    print("===========================")

# ==================== MAIN ====================
if __name__ == '__main__':
    run_test_auto()
