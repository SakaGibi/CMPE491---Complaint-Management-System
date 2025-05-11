import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';
import { NgChartsModule } from 'ng2-charts';
import { ChartData, ChartOptions } from 'chart.js';

@Component({
  selector: 'app-management-panel',
  standalone: true,
  imports: [CommonModule, FormsModule, NgChartsModule],
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent implements OnInit {

  complaintList: any[] = [];
  suggestionList: any[] = [];
  isComplaintModalOpen: boolean = false;
  selectedComplaint: any = null;
  selectedComplaintStatus: string | null = null;
  selectedStatus: string = '';
  selectedCategory: string = '';
  selectedIsTrackable: string = '';
  selectedSortOption: string = '';
  selectedTrackable: string = '';
  isSuggestionModalOpen: boolean = false;
  selectedSuggestion: any = null;
  chartData: { category: string; count: number }[] = [];
  readonly ALL_CATEGORIES = [
    'bakım ve onarım',
    'temizlik',
    'ortak alan kullanımı',
    'güvenlik',
    'yönetim',
    'gürültü'
  ];
  isChartModalOpen: boolean = false;
  chartRange: string = '';
  barChartLabels: string[] = [];
  barChartData: ChartData<'bar'> = {
    labels: [],
    datasets: [
      {
        label: 'Complaint Count',
        data: [],
        backgroundColor: 'rgba(54, 162, 235, 0.6)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 1
      }
    ]
  };
  barChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  };
  isTrendModalOpen: boolean = false;
  trendRange: string = '';
  trendCategory: string = '';
  lineChartLabels: string[] = [];
  lineChartData: ChartData<'line'> = {
    labels: [],
    datasets: [
      {
        label: 'Daily Complaints',
        data: [],
        borderColor: 'rgba(75, 192, 192, 1)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.3
      }
    ]
  };
  lineChartOptions: ChartOptions = {
    responsive: true,
    scales: {
      x: {
        type: 'time',
        time: {
          unit: 'day',
          tooltipFormat: 'MMM d',
          displayFormats: {
            day: 'MMM d'
          }
        },
        title: {
          display: true,
          text: 'Date'
        }
      },
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Number of Complaints'
        }
      }
    }
  };

  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.fetchSuggestions();
    this.fetchComplaints();
    this.fetchComplaintStatistics();
    this.fetchComplaintTrends();
    this.fetchReports();
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }

  fetchComplaints(): void {
    const params: any = {
      type: 'complaint'
    };
  
    if (this.selectedStatus) params.status = this.selectedStatus;
    if (this.selectedCategory) params.category = this.selectedCategory;
    if (this.selectedTrackable) params.isTrackable = this.selectedTrackable;
  
    console.log('[fetchComplaints] params:', params);
  
    this.apiService.getComplaints(params).subscribe({
      next: (res) => {
        console.log('[fetchComplaints] Gelen yanıt:', res);
        this.complaintList = this.sortComplaintsLocally(res, this.selectedSortOption);
      },
      error: (err) => {
        console.error('[fetchComplaints] API hatası:', err);
      }
    });
  }
  
  sortComplaintsLocally(complaints: any[], sortBy: string): any[] {
    if (!Array.isArray(complaints)) return [];
  
    switch (sortBy) {
      case 'newest':
        return complaints.sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      case 'oldest':
        return complaints.sort((a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      case 'status':
        const statusOrder: { [key: string]: number } = {
          new: 1,
          in_progress: 2,
          resolved: 3,
          reopened: 4,
          closed: 5
        };
        return complaints.sort((a, b) =>
          (statusOrder[a.status] || 99) - (statusOrder[b.status] || 99)
        );
      default:
        return complaints;
    }
  }
  fetchComplaintDetails(id: number): void {
    console.log(`[fetchComplaintDetails] ID ${id} için detaylar alınıyor...`);
    this.apiService.getComplaintById(id).subscribe({
      next: (res) => {
        console.log('[fetchComplaintDetails] Detaylar geldi:', res);
        this.selectedComplaint = res;
      },
      error: (err) => {
        console.error('[fetchComplaintDetails] API hatası:', err);
      }
    });
  }

  openComplaintModal(complaintId: number): void {
    console.log('[openComplaintModal] Açılan ID:', complaintId);
  
    this.apiService.getComplaintById(complaintId).subscribe({
      next: (res) => {
        console.log('[openComplaintModal] Şikayet verisi:', res);
        this.selectedComplaint = res;
        this.selectedComplaintStatus = res.status;
        this.isComplaintModalOpen = true;
      },
      error: (err) => {
        console.error('[openComplaintModal] Hata:', err);
      }
    });
  }

  closeComplaintModal(): void {
    this.isComplaintModalOpen = false;
    this.selectedComplaint = null;
  }

  updateComplaintStatus(): void {
    if (!this.selectedComplaint || !this.selectedComplaint.id || !this.selectedComplaintStatus) {
      console.warn('[updateComplaintStatus] Gerekli bilgiler eksik.');
      return;
    }
  
    console.log('[updateComplaintStatus] Gönderilen:', {
      id: this.selectedComplaint.id,
      status: this.selectedComplaintStatus
    });
  
    this.apiService.updateComplaintStatus(this.selectedComplaint.id, this.selectedComplaintStatus).subscribe({
      next: (res) => {
        console.log('[updateComplaintStatus] Güncelleme başarılı:', res);
        this.selectedComplaint.status = this.selectedComplaintStatus;
        alert('Şikayet durumu başarıyla güncellendi.');
      },
      error: (err) => {
        console.error('[updateComplaintStatus] Hata:', err);
        alert('Durum güncellenemedi.');
      }
    });
  }
  
  
  deleteComplaint(): void {
    if (!this.selectedComplaint) return;
  
    const confirmDelete = confirm('Bu şikayeti silmek istediğinize emin misiniz?');
    if (!confirmDelete) return;
  
    this.apiService.deleteComplaint(this.selectedComplaint.id).subscribe({
      next: (res) => {
        console.log('[deleteComplaint] Başarılı:', res);
        this.complaintList = this.complaintList.filter(c => c.id !== this.selectedComplaint?.id);
        this.selectedComplaint = null;
        this.isComplaintModalOpen = false;
        alert('Şikayet silindi.');
      },
      error: (err) => {
        console.error('[deleteComplaint] Hata:', err);
        alert('Şikayet silinemedi.');
      }
    });
  }

  fetchSuggestions(): void {
    console.log('[fetchSuggestions] Öneri API çağrısı başlatıldı...');
    this.apiService.getSuggestions().subscribe({
      next: (res) => {
        console.log('[fetchSuggestions] Gelen yanıt:', res);
        this.suggestionList = res;
      },
      error: (err) => {
        console.error('[fetchSuggestions] API hatası:', err);
      }
    });
  }

  deleteSuggestion(): void {
    if (!this.selectedSuggestion) return;
  
    const confirmDelete = confirm('Bu öneriyi silmek istediğinize emin misiniz?');
    if (!confirmDelete) return;
  
    this.apiService.deleteComplaint(this.selectedSuggestion.id).subscribe({
      next: (res) => {
        console.log('[deleteSuggestion] Başarılı:', res);
        this.suggestionList = this.suggestionList.filter(s => s.id !== this.selectedSuggestion?.id);
        this.selectedSuggestion = null;
        this.isSuggestionModalOpen = false;
        alert('Öneri silindi.');
      },
      error: (err) => {
        console.error('[deleteSuggestion] Hata:', err);
        alert('Öneri silinemedi.');
      }
    });
  }

  openSuggestionModal(suggestion: any): void {
    this.selectedSuggestion = suggestion;
    this.isSuggestionModalOpen = true;
  }
  
  closeSuggestionModal(): void {
    this.selectedSuggestion = null;
    this.isSuggestionModalOpen = false;
  }
  
  fetchComplaintStatistics(range: string = ''): void {
    console.log('[fetchComplaintStatistics] API çağrısı başlatıldı...', { range });
  
    this.apiService.getComplaintStatistics(range).subscribe({
      next: (res) => {
        console.log('[fetchComplaintStatistics] Gelen yanıt:', res);
  
        const categoryMap: { [key: string]: number } = {};
        this.ALL_CATEGORIES.forEach(cat => categoryMap[cat] = 0);
  
        res.forEach((item: any) => {
          const cat = item.category?.toLowerCase();
          if (cat && categoryMap.hasOwnProperty(cat)) {
            categoryMap[cat] = item.count;
          }
        });
  
        this.chartData = this.ALL_CATEGORIES.map(category => ({
          category,
          count: categoryMap[category]
        }));
  
        // 🔽 Bar chart datasını burada güncelliyoruz
        this.barChartData = {
          labels: this.chartData.map(c => c.category),
          datasets: [
            {
              label: 'Complaint Count',
              data: this.chartData.map(c => c.count),
              backgroundColor: 'rgba(54, 162, 235, 0.6)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            }
          ]
        };
      },
      error: (err) => {
        console.error('[fetchComplaintStatistics] API hatası:', err);
      }
    });
  }
  
  refreshComplaintsAndChart(): void {
    console.log('[refreshComplaintsAndChart] Güncelleme başlatıldı...');
    this.fetchComplaints();
    this.fetchComplaintStatistics(this.chartRange);
    this.fetchComplaintTrends(this.trendRange, this.trendCategory);
  }
  
  openChartModal(): void {
    this.isChartModalOpen = true;
    this.fetchComplaintStatistics();
  }
  
  
  closeChartModal(): void {
    this.isChartModalOpen = false;
  }

  fetchComplaintTrends(range: string = '', category: string = ''): void {
    const params: any = {};
    if (range) params.range = range;
    if (category) params.category = category;
  
    console.log('[fetchComplaintTrends] Params:', params);
  
    this.apiService.getComplaintTrends(params).subscribe({
      next: (res) => {
        console.log('[fetchComplaintTrends] Gelen yanıt:', res);
  
        this.lineChartData = {
          labels: res.map((item: any) => item.day), // 🔥 ISO string kullan!
          datasets: [
            {
              label: 'Daily Complaints',
              data: res.map((item: any) => item.count),
              fill: false,
              borderColor: '#007bff',
              tension: 0.3
            }
          ]
        };
  
        console.log('📊 lineChartData:', this.lineChartData);
      },
      error: (err) => {
        console.error('[fetchComplaintTrends] Hata:', err);
      }
    });
  }

  openTrendModal(): void {
    this.isTrendModalOpen = true;
    this.fetchComplaintTrends(this.trendRange, this.trendCategory);
  }
  
  closeTrendModal(): void {
    this.isTrendModalOpen = false;
  }

  // RAPORLAR
  reportList: any[] = [];
  selectedReport: any = null;
  isReportModalOpen: boolean = false;
  isLoadingReport: boolean = false;
  newReportFilters: any = {
    category: '',
    status: '',
    type: 'complaint',         
    isTrackable: '',
    date_from: '',
    date_to: ''
  };
  newReportType: string = 'Genel Özet';
  newReportName: string = '';


  fetchReports(): void {
    this.apiService.listReports().subscribe({
      next: (res) => {
       console.log('[fetchReports] Rapor listesi:', res);
       this.reportList = res;
      },
      error: (err) => {
       console.error('[fetchReports] Hata:', err);
        alert('Raporlar alınamadı.');
      }
    });
  }

  private cleanFilters(filters: any): any {
    const cleaned: any = {};
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== '' && value !== null && value !== undefined) {
        cleaned[key] = value;
      }
    });
    return cleaned;
  }

  generateNewReport(): void {
    if (!this.newReportName.trim()) {
      alert('Lütfen bir rapor ismi giriniz.');
      return;
    }

    const cleanedFilters = this.cleanFilters(this.newReportFilters);

    const payload = {
      reportType: this.newReportName.trim(),
      filters: cleanedFilters
    };

    console.log('[generateNewReport] Gönderilen:', payload);
    this.isLoadingReport = true;

    this.apiService.generateReport(payload).subscribe({
      next: (res) => {
        console.log('[generateNewReport] Başarılı:', res);
        this.fetchReports();
        this.newReportName = '';
        this.isLoadingReport = false;
        alert('Rapor başarıyla oluşturuldu.');
      },
      error: (err) => {
        console.error('[generateNewReport] Hata:', err);
        alert('Rapor oluşturulurken bir hata oluştu.');
        this.isLoadingReport = false;
      }
    });
  }

  openReportDetail(reportId: number): void {
    this.apiService.getReportById(reportId).subscribe({
      next: (res) => {
        console.log('[openReportDetail] Rapor:', res);
        this.selectedReport = res;
        this.isReportModalOpen = true;
      },
      error: (err) => {
        console.error('[openReportDetail] Hata:', err);
        alert('Rapor alınamadı.');
      }
    });
  }

  deleteReport(reportId: number): void {
    const onay = confirm('Bu raporu silmek istediğinizden emin misiniz?');
    if (!onay) return;

    this.apiService.deleteReport(reportId).subscribe({
      next: (res) => {
        console.log('[deleteReport] Silindi:', res);
        this.reportList = this.reportList.filter(r => r.id !== reportId);
        alert('Rapor silindi.');
      },
      error: (err) => {
        console.error('[deleteReport] Hata:', err);
        alert('Rapor silinemedi.');
      }
    });
  }

  closeReportModal(): void {
    this.selectedReport = null;
    this.isReportModalOpen = false;
  }
}
