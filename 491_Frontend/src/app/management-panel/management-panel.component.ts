import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-management-panel',
  imports: [CommonModule, FormsModule],
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent {

  constructor(private router: Router){}
  
  isDetailsModalOpen = false;
  currentDetailsType: 'chart' | 'graph' | 'complaint' | 'suggestion' | null = null; 
  selectedComplaintStatus: string | null = null;
  selectedSuggestionStatus: string | null = null; 

  goToSupport() {
    this.router.navigate(['/helpSupport']);
  }
  goToMainMenu() {
    this.router.navigate(['/mainMenu']);
  }

  selectedComplaint: {
    id: number;
    status: string;
    description: string;
    department?: string;
    tracking?: boolean;
  } | null = null;

  selectedSuggestion: {
    id: number;
    description: string;
    department?: string;
    status: string;
  } | null = null;

  complaints = [
    {
      id: 1,
      status: 'pending',
      description: 'Complaint 1 details...',
      department: 'IT',
      tracking: true
    },
    {
      id: 2,
      status: 'resolved',
      description: 'Complaint 2 details...',
      department: 'HR',
      tracking: false
    },
    {
      id: 3,
      status: 'pending',
      description: 'Complaint 3 details...',
      department: 'Customer Service',
      tracking: true
    }
  ];

  suggestions = [
    {
      id: 1,
      description: 'Suggestion 1 details...',
      department: 'IT',
      status: 'pending'
    },
    {
      id: 2,
      description: 'Suggestion 2 details...',
      department: 'HR',
      status: 'implemented'
    },
    {
      id: 3,
      description: 'Suggestion 3 details...',
      department: 'Customer Service',
      status: 'pending'
    }
  ];

  openDetails(type: 'chart' | 'graph') {
    this.isDetailsModalOpen = true;
    this.currentDetailsType = type;
  }

  openComplaintDetails(complaint: any) {
    this.isDetailsModalOpen = true;
    this.currentDetailsType = 'complaint';
    this.selectedComplaint = complaint ? { ...complaint } : null;
    if (this.selectedComplaint) {
      this.selectedComplaintStatus = this.selectedComplaint.status;
    }
  }

  openSuggestionDetails(suggestion: any) {
    this.isDetailsModalOpen = true;
    this.currentDetailsType = 'suggestion';
    this.selectedSuggestion = suggestion ? { ...suggestion } : null;
    if (this.selectedSuggestion) {
      this.selectedSuggestionStatus = this.selectedSuggestion.status;
    }
  }

  closeDetails() {
    this.isDetailsModalOpen = false;
    this.currentDetailsType = null;
    this.selectedComplaint = null;
    this.selectedSuggestion = null;
    this.selectedComplaintStatus = null;
    this.selectedSuggestionStatus = null;
  }
}
