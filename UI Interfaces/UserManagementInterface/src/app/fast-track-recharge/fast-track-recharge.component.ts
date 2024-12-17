import { Component } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../shared/auth.service';

@Component({
  selector: 'app-fast-track-recharge',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './fast-track-recharge.component.html',
  styleUrl: './fast-track-recharge.component.css'
})
export class FastTrackRechargeComponent {
  transHist = false;
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
     rechargeForm = new FormGroup({
        tag: new FormControl('', {
          validators: [Validators.required],
        }),
        amount: new FormControl('',{
          validators: [Validators.required]
        })
      });

    constructor(private authService: AuthService) {}

    ngOnInit() {
      this.authService.fetchFastTag().subscribe(
        (respData)=>{
          console.log(respData);
          this.fastTrackReturn = respData;
        }
      )
    }

    onRecharge() {
      if (this.rechargeForm.valid) {
        this.authService.rechargeFastTag(this.rechargeForm.value.tag!,this.rechargeForm.value.amount!).subscribe(
          (respData)=>{
            console.log(respData);
            alert(this.rechargeForm.value.tag+" has Successfully Recharged");
            let item = this.fastTrackReturn.find((obj:any) => obj.id === this.rechargeForm.value.tag);
            item.balance = parseFloat(item.balance) + parseFloat(this.rechargeForm.value.amount!) 
          }
        )
      }
    }

    onHistory(tagId:string) {
      this.authService.fetchHistory(tagId).subscribe(
        (respData)=>{
          console.log(respData);
          this.transHist = true;
          this.transactionHistory = respData;
        }
      )
    }
}
