import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-recharge-fastag',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './recharge-fastag.component.html',
  styleUrl: './recharge-fastag.component.css',
})
export class RechargeFastagComponent implements OnInit {
  rechargeForm = new FormGroup({
    tag: new FormControl('', {
      validators: [Validators.required],
    }),
    amount: new FormControl(0, {
      validators: [Validators.required],
    }),
  });
  constructor(private authService: AuthService) {}

  fastTrackReturn: any = [
    {
      id: '1',
      vehicleId: '01',
      status: 'Active',
      balance: '1000',
    },
    {
      id: '2',
      vehicleId: '02',
      status: 'Blocked',
      balance: '101',
    },
    {
      id: '3',
      vehicleId: '03',
      status: 'Active',
      balance: '11',
    },
  ];

  ngOnInit() {
    this.authService.fetchFastTag().subscribe((respData) => {
      console.log(respData);
      this.fastTrackReturn = respData;
    });
  }

  onRecharge(){}

  setAmount(amount:number){
    this.rechargeForm.controls['amount'].setValue(amount)
  }

  rechargeFastage(){
    let amount = this.rechargeForm.controls['amount'].value as number
    let tagId = this.rechargeForm.controls['tag'].value as string
    this.authService.rechargeFastTag(tagId,amount).subscribe({
      next:(data)=>{
        console.log(data)
      }
    })
  }
}
