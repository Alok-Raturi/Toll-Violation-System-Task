import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-transaction-history',
  standalone: true,
  imports: [DatePipe],
  templateUrl: './transaction-history.component.html',
  styleUrl: './transaction-history.component.css'
})
export class TransactionHistoryComponent implements OnInit {
  transactionHistory:any[]=[];
  tagid:string=""

  constructor(private activatedRoute: ActivatedRoute,private authService: AuthService){}

  ngOnInit(): void {
    this.activatedRoute.params.subscribe(
      (params)=>{
        this.authService.fetchHistory(params['id']).subscribe(
          (respData:any)=>{
            this.transactionHistory = respData
            this.tagid=params['id']
          }
        );
      }
     );
  }
}
