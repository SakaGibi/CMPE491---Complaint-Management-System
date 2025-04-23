import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-management-panel',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent implements OnInit {

  complaintList: any[] = [];
  isComplaintModalOpen: boolean = false;
  selectedComplaint: any = null;
  selectedComplaintStatus: string | null = null;
  selectedStatus: string = '';
  selectedCategory: string = '';
  selectedIsTrackable: string = '';
  selectedSortOption: string = '';
  selectedTrackable: string = '';

  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    console.log('[ManagementPanel] ngOnInit çalıştı.');
    this.fetchComplaints();
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

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }
}
