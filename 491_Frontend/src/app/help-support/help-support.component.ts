import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-help-support',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './help-support.component.html',
  styleUrls: ['./help-support.component.css']
})

export class HelpSupportComponent implements OnInit {

  faqs: any[] = [];

  constructor(
    private router: Router,
    private apiService: ApiService
  ) {}

  ngOnInit(): void {
    this.loadFAQs();
  }

  loadFAQs(): void {
    this.apiService.getFAQs().subscribe({
      next: (res) => {
        console.log('[FAQ] Veriler:', res);
        this.faqs = res;
      },
      error: (err) => {
        console.error('[FAQ] Hata:', err);
      }
    });
  }

  goToMainMenu(): void {
    this.router.navigate(['/mainMenu']);
  }
}
