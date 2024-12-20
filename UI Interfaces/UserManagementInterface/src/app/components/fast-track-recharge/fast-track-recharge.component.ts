import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { DatePipe } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-fast-track-recharge',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './fast-track-recharge.component.html',
  styleUrl: './fast-track-recharge.component.css'
})
export class FastTrackRechargeComponent {
  transactionHistory:any;
  fastTrackReturn:any = [
    {
      id:"1",
      vehicleId:"01",
      status:"Active",
      balance:"1000"
    },
    {
      id:"2",
      vehicleId:"02",
      status:"Blocked",
      balance:"101"
    },
    {
      id:"3",
      vehicleId:"03",
      status:"Active",
      balance:"11"
    },
    ];

    constructor(private authService: AuthService,private router: Router) {}

    ngOnInit() {
      this.authService.fetchFastTag().subscribe(
        (respData)=>{
          console.log(respData);
          this.fastTrackReturn = respData;
        }
      )
    }


    onHistory(tagId:string) {
      this.router.navigate([`/dashboard/transaction-history/${tagId}`])
    }

}
