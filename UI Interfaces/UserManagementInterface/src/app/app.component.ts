import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { AuthService } from './shared/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'TollTracker';
  constructor(private authService: AuthService) {  }

  ngOnInit() {
    this.authService.autoLogin();
  }
}
