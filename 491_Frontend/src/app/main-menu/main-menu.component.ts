import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-main-menu',
  imports: [FormsModule, CommonModule],
  templateUrl: './main-menu.component.html',
  styleUrl: './main-menu.component.css'
})
export class MainMenuComponent {

  complaintNumber: string = '';
  complaintStatus: string = '';
  isTracking: boolean = false;

  constructor(private router: Router){}

  writeComplaintOrSuggestion(){
    // doldurulucak. 
  }

  toggleEmailInput() {
    const checkbox = document.getElementById('trackCheckBox') as HTMLInputElement | null;
    const emailInput = document.getElementById('emailInputContainer') as HTMLElement | null;

    if (checkbox && emailInput) { 
      if (checkbox.checked) {
        emailInput.style.display = 'block'; 
      } else {
        emailInput.style.display = 'none'; 
      }
    }
  }

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }

  goToManagementPanelLogin() {
    this.router.navigate(['/managementPanelLogin']);
  }

  openModal() {
    const modal = document.getElementById('complaintModal');
    if (modal) {
      modal.style.display = 'flex';
    }
  }
  
  closeModal() {
    const modal = document.getElementById('complaintModal');
    if (modal) {
      modal.style.display = 'none';
    }
  }

  trackComplaint(event: Event) {
    event.preventDefault();
    if (this.complaintNumber.trim() !== '') {
      this.complaintStatus = `Complaint #${this.complaintNumber} is currently being processed.`; // Dinamik veri buraya bağlanabilir
      this.isTracking = true;
    } else {
      this.complaintStatus = 'Please enter a valid complaint number.';
    }
  }

  resetModal() {
    this.complaintNumber = '';
    this.complaintStatus = '';
    this.isTracking = false;
  }
  

}
