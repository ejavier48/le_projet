import { Component, OnInit } from '@angular/core';
//para recibir paramteros
import { ActivatedRoute } from "@angular/router";
//importo el servicio para conectarme a flask
import { MensajeroFlaskService } from '../mensajero-flask.service';
//para moverme entre pantallas
import { Router } from "@angular/router";
//para mostrar el loading
import { LoadingController } from '@ionic/angular';
//mostrar alerta
import { AlertController } from '@ionic/angular';


@Component({
  selector: 'app-consulta',
  templateUrl: './consulta.page.html',
  styleUrls: ['./consulta.page.scss'],
})
export class ConsultaPage implements OnInit {
  ipAdd:string;
  port:string;
  data:any;
  constructor(private activatedRoute: ActivatedRoute,
    private FlaskService: MensajeroFlaskService,
    private router: Router,
    private loadcont: LoadingController,
    public alertController: AlertController) { }

  ngOnInit() {
    this.ipAdd = this.activatedRoute.snapshot.paramMap.get('ipAdd');
    this.port = this.activatedRoute.snapshot.paramMap.get('port');
    console.log(this.ipAdd);
    console.log(this.port);

    this.getData();
  }

  async getData() {

    const loading = await this.loadcont.create({
      message: 'Conectando'
    });
    await loading.present();

    this.FlaskService.getData(this.ipAdd,this.port)
      .subscribe(res => {
        console.log(res);
        this.data = res;

          loading.dismiss();
      }, err => {
        console.log("error:"+JSON.stringify(err));
        this.router.navigate(['/']);
          loading.dismiss();
          this.presentAlert(JSON.stringify(err));
      });
  }

  async presentAlert(mensaje:string) {
  const alert = await this.alertController.create({
    header: 'Error de conexion',
    subHeader: 'No se ha podido establer la conexion con el servidor',
    message: mensaje,
    buttons: ['OK']
  });

  await alert.present();
}

}
