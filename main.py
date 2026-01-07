import csv
import threading

class Process:
    def __init__(self, pid, arrival, burst, priority):
        self.pid = pid
        self.arrival = int(arrival)
        self.burst = int(burst)
        self.priority = self.map_p(priority)
        self.remaining_time = int(burst)
        self.completion_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0

    def map_p(self, p_str):
        p_str = p_str.lower().strip()
        if 'high' in p_str: return 1
        if 'normal' in p_str: return 2
        return 3

def csv_oku(dosya_adi):
    liste = []
    with open(dosya_adi, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        for satir in reader:
            if satir:
                liste.append(Process(satir[0], satir[1], satir[2], satir[3]))
    return liste

def rapor_yaz(algo_adi, durum, prosesler, gantt, cs_sayisi):
    wts = [p.waiting_time for p in prosesler]
    tats = [p.turnaround_time for p in prosesler]
    throughput = [sum(1 for p in prosesler if p.completion_time <= t) for t in [50, 100, 150, 200]]
    toplam_burst = sum(p.burst for p in prosesler)
    verimlilik = (toplam_burst / (toplam_burst + (cs_sayisi * 0.001))) * 100
    
    with open(f"{durum}_{algo_adi}.txt", "w", encoding="utf-8") as f:
        f.write(f"--- {algo_adi} Zaman Tablosu ---\n")
        f.write("\n".join(gantt) + "\n\n")
        f.write(f"Maksimum Bekleme: {max(wts)}\nOrtalama Bekleme: {sum(wts)/len(wts):.2f}\n")
        f.write(f"Maksimum Tamamlanma: {max(tats)}\nOrtalama Tamamlanma: {sum(tats)/len(tats):.2f}\n")
        f.write(f"Throughput (50, 100, 150, 200): {throughput}\n")
        f.write(f"CPU Verimliligi: %{verimlilik:.4f}\n")
        f.write(f"Toplam Baglam Degistirme Sayisi: {cs_sayisi}\n")

def fcfs(prosesler, durum):
    prosesler.sort(key=lambda x: x.arrival)
    zaman, cs, gantt = 0, 0, []
    for p in prosesler:
        if zaman < p.arrival:
            gantt.append(f"[{zaman}]--IDLE--[{p.arrival}]")
            zaman = p.arrival
        bas = zaman
        zaman += p.burst
        p.completion_time = zaman
        p.turnaround_time = zaman - p.arrival
        p.waiting_time = p.turnaround_time - p.burst
        gantt.append(f"[{bas}]--{p.pid}--[{zaman}]")
        cs += 1
    rapor_yaz("FCFS", durum, prosesler, gantt, cs)

def sjf_np(prosesler, durum):
    zaman, cs, gantt, tamam, kopya = 0, 0, [], [], list(prosesler)
    while len(tamam) < len(prosesler):
        bekleyen = [p for p in kopya if p.arrival <= zaman]
        if not bekleyen:
            zaman += 1
            continue
        secilen = min(bekleyen, key=lambda x: x.burst)
        bas = zaman
        zaman += secilen.burst
        secilen.completion_time = zaman
        secilen.turnaround_time = zaman - secilen.arrival
        secilen.waiting_time = secilen.turnaround_time - secilen.burst
        gantt.append(f"[{bas}]--{secilen.pid}--[{zaman}]")
        cs += 1
        tamam.append(secilen)
        kopya.remove(secilen)
    rapor_yaz("NonPre_SJF", durum, tamam, gantt, cs)

def sjf_p(prosesler, durum):
    zaman, cs, gantt, tamam, kopya = 0, 0, [], [], list(prosesler)
    aktif = None
    while len(tamam) < len(prosesler):
        bekleyen = [p for p in kopya if p.arrival <= zaman]
        if not bekleyen:
            zaman += 1
            continue
        secilen = min(bekleyen, key=lambda x: x.remaining_time)
        if aktif != secilen:
            cs += 1
            aktif = secilen
        bas = zaman
        zaman += 1
        secilen.remaining_time -= 1
        gantt.append(f"[{bas}]--{secilen.pid}--[{zaman}]")
        if secilen.remaining_time == 0:
            secilen.completion_time = zaman
            secilen.turnaround_time = zaman - secilen.arrival
            secilen.waiting_time = secilen.turnaround_time - secilen.burst
            tamam.append(secilen)
            kopya.remove(secilen)
            aktif = None
    rapor_yaz("Preemptive_SJF", durum, tamam, gantt, cs)

def round_robin(prosesler, durum, q=4):
    zaman, cs, gantt, tamam = 0, 0, [], []
    kuyruk = []
    kopya = sorted(list(prosesler), key=lambda x: x.arrival)
    while len(tamam) < len(prosesler):
        for p in list(kopya):
            if p.arrival <= zaman:
                kuyruk.append(p)
                kopya.remove(p)
        if not kuyruk:
            zaman += 1
            continue
        p = kuyruk.pop(0)
        cs += 1
        bas = zaman
        sure = min(p.remaining_time, q)
        zaman += sure
        p.remaining_time -= sure
        gantt.append(f"[{bas}]--{p.pid}--[{zaman}]")
        for np in list(kopya):
            if np.arrival <= zaman:
                kuyruk.append(np)
                kopya.remove(np)
        if p.remaining_time > 0:
            kuyruk.append(p)
        else:
            p.completion_time = zaman
            p.turnaround_time = zaman - p.arrival
            p.waiting_time = p.turnaround_time - p.burst
            tamam.append(p)
    rapor_yaz("RoundRobin", durum, tamam, gantt, cs)

def priority_np(prosesler, durum):
    zaman, cs, gantt, tamam, kopya = 0, 0, [], [], list(prosesler)
    while len(tamam) < len(prosesler):
        bekleyen = [p for p in kopya if p.arrival <= zaman]
        if not bekleyen:
            zaman += 1
            continue
        secilen = min(bekleyen, key=lambda x: x.priority)
        bas = zaman
        zaman += secilen.burst
        secilen.completion_time = zaman
        secilen.turnaround_time = zaman - secilen.arrival
        secilen.waiting_time = secilen.turnaround_time - secilen.burst
        gantt.append(f"[{bas}]--{secilen.pid}--[{zaman}]")
        cs += 1
        tamam.append(secilen)
        kopya.remove(secilen)
    rapor_yaz("NonPre_Priority", durum, tamam, gantt, cs)

def priority_p(prosesler, durum):
    zaman, cs, gantt, tamam, kopya = 0, 0, [], [], list(prosesler)
    aktif = None
    while len(tamam) < len(prosesler):
        bekleyen = [p for p in kopya if p.arrival <= zaman]
        if not bekleyen:
            zaman += 1
            continue
        secilen = min(bekleyen, key=lambda x: x.priority)
        if aktif != secilen:
            cs += 1
            aktif = secilen
        bas = zaman
        zaman += 1
        secilen.remaining_time -= 1
        gantt.append(f"[{bas}]--{secilen.pid}--[{zaman}]")
        if secilen.remaining_time == 0:
            secilen.completion_time = zaman
            secilen.turnaround_time = zaman - secilen.arrival
            secilen.waiting_time = secilen.turnaround_time - secilen.burst
            tamam.append(secilen)
            kopya.remove(secilen)
            aktif = None
    rapor_yaz("Preemptive_Priority", durum, tamam, gantt, cs)

def senaryo_baslat(dosya, durum):
    algolar = [fcfs, sjf_np, sjf_p, round_robin, priority_np, priority_p]
    is_parcaciklari = []
    for algo in algolar:
        t = threading.Thread(target=algo, args=(csv_oku(dosya), durum))
        is_parcaciklari.append(t)
        t.start()
    for t in is_parcaciklari:
        t.join()

if __name__ == "__main__":
    senaryo_baslat("case1.csv", "case1")
    senaryo_baslat("case2.csv", "case2")
    print("Tum algoritmalar ve senaryolar tamamlandi.")