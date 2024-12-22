import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-challan-page',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './challan-page.component.html',
  styleUrl: './challan-page.component.css',
})
export class ChallanPageComponent {
  challanReturn: any = [];
  vehicleId: string = '';

  constructor(
    private activatedRoute: ActivatedRoute,
    private authService: AuthService
  ) {}


  ngOnInit() {
    this.activatedRoute.params.subscribe((params) => {
      this.authService.fetchChallan(params['id']).subscribe((respData) => {
        this.vehicleId = params['id'];
        this.challanReturn = respData;
      });
    });
  }

  getDueDate(due_time: number) {
    return new Date(due_time * 1000);
  }

  payAChallan(id: string) {
    return this.authService.paySingleChallan(id).subscribe({
      next: (respData) => {
        this.authService.fetchChallan(this.vehicleId).subscribe({
          next: (updatedChallans) => {
            this.challanReturn = updatedChallans;
          },
        });
      },
    });
  }

  payAllChallan(vid: string) {
    return this.authService.payAllChallan(vid).subscribe({
      next: (respData) => {
        this.authService.fetchChallan(this.vehicleId).subscribe({
          next: (updatedChallans) => {
            this.challanReturn = updatedChallans;
          },
        });
      },
    });
  }
}
