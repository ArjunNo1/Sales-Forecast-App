import { Component } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-forms',
  templateUrl: './forms.component.html',
  styleUrls: ['./forms.component.css']
})
export class FormsComponent {

  file: File | null = null;
  num: number = 0;
  
  response: any;
  constructor(private http: HttpClient) { }

  onFileChange(event: any) {
    this.file = event.target.files.item(0);
  }

  onSubmit() {
    const formData = new FormData();
    formData.append('file', this.file!);
    formData.append('num', this.num.toString());

    this.http.post('http://localhost:5000/form', formData).subscribe(
      (response:any) => this.response = response,
      (error) => console.log(error)
    );
  }  
  
}