import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';
import { DatePipe, UpperCasePipe } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-fast-track-recharge',
  standalone: true,
  imports: [ReactiveFormsModule, UpperCasePipe],
  templateUrl: './fast-track-recharge.component.html',
  styleUrl: './fast-track-recharge.component.css'
})
export class FastTrackRechargeComponent {
  transactionHistory:any;
  fastTrackReturn:any = [
    {
      id:"1",
      vehicleId:"01",
      status:"Valid",
      balance:"1000"
    },
    {
      id:"2",
      vehicleId:"02",
      status:"Invalid",
      balance:"101"
    },
    {
      id:"3",
      vehicleId:"03",
      status:"Invalid",
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
