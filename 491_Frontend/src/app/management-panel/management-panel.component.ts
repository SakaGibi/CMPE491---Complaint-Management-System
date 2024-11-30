import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-management-panel',
  imports: [CommonModule, FormsModule],
  templateUrl: './management-panel.component.html',
  styleUrls: ['./management-panel.component.css']
})
export class ManagementPanelComponent {
  isDetailsModalOpen = false;
  currentDetailsType: 'chart' | 'graph' | 'complaint' | null = null;
  selectedComplaintStatus: string | null = null;

  selectedComplaint: {
    id: number;
    status: string;
    description: string;
    department?: string;
    tracking?: boolean;
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

  closeDetails() {
    this.isDetailsModalOpen = false;
    this.currentDetailsType = null;
    this.selectedComplaint = null;
    this.selectedComplaintStatus = null; 

  }
}
