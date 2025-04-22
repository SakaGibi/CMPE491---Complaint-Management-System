import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-management-panel',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent implements OnInit {

  complaintList: any[] = [];
  isComplaintModalOpen: boolean = false;
  selectedComplaint: any = null;

  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    console.log('[ManagementPanel] ngOnInit çalıştı.');
    this.fetchComplaints();
  }

  fetchComplaints(): void {
    console.log('[fetchComplaints] Şikayetler API çağrısı başlatıldı...');
    this.apiService.getComplaints().subscribe({
      next: (res) => {
        console.log('[fetchComplaints] Gelen yanıt:', res);
        this.complaintList = res;
      },
      error: (err) => {
        console.error('[fetchComplaints] API hatası:', err);
      }
    });
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

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }
}
