import flet as ft
from docxtpl import DocxTemplate
import os
import datetime
import shutil

def main(page: ft.Page):
    # Configuración básica
    page.title = "DocPol Mobile"
    page.scroll = "adaptive"
    page.padding = 20
    page.theme_mode = "light" 

    # Variable para guardar la ruta temporal del archivo generado
    archivo_temporal = [""]

    # --- MENSAJES ---
    def mostrar_mensaje(mensaje, color):
        page.snack_bar = ft.SnackBar(ft.Text(mensaje), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    # --- GUARDADO ---
    def guardar_archivo_final(e: ft.FilePickerResultEvent):
        if e.path:
            try:
                # Copiamos el archivo temporal a la ruta que eligió el usuario
                shutil.copy(archivo_temporal[0], e.path)
                mostrar_mensaje(f"✅ Guardado en: {e.path}", "green")
            except Exception as ex:
                mostrar_mensaje(f"❌ Error al guardar: {str(ex)}", "red")
        else:
            mostrar_mensaje("⚠️ Guardado cancelado", "orange")

    file_picker = ft.FilePicker(on_result=guardar_archivo_final)
    page.overlay.append(file_picker)

    # --- LÓGICA ---
    def generar_documento(e):
        # CAMBIO IMPORTANTE: Ahora buscamos en la carpeta assets
        ruta_plantilla = "assets/plantilla.docx"

        # Verificación extra por si acaso
        if not os.path.exists(ruta_plantilla):
            # A veces en Android la ruta assets es relativa directa
            if os.path.exists("plantilla.docx"): 
                 ruta_plantilla = "plantilla.docx"
            else:
                 # Si falla, intentamos una ruta segura pero avisamos
                 mostrar_mensaje(f"❌ No encuentro 'assets/plantilla.docx'", "red")
                 # (En Flet empaquetado, assets suele estar en la raiz de ejecución)
        
        datos = {
            "numero_atestado": txt_atestado.value,
            "fecha": txt_fecha.value,
            "nombre": txt_nombre.value,
            "dni": txt_dni.value,
            "delito": dd_delito.value
        }

        try:
            # Cargamos la plantilla
            doc = DocxTemplate(ruta_plantilla)
            doc.render(datos)
            
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            nombre_temp = f"Atestado_{timestamp}.docx"
            
            # Guardamos primero en la carpeta temporal de la app
            doc.save(nombre_temp)
            archivo_temporal[0] = nombre_temp
            
            # Abrimos el diálogo para que el usuario lo guarde en su móvil
            file_picker.save_file(dialog_title="Guardar Atestado", file_name=nombre_temp)
            
        except Exception as ex:
            mostrar_mensaje(f"Error generando: {str(ex)}", "red")

    # --- CAMPOS ---
    txt_atestado = ft.TextField(label="Nº Atestado", border="outline")
    txt_fecha = ft.TextField(label="Fecha", value=datetime.date.today().strftime("%d/%m/%Y"), border="outline")
    
    dd_delito = ft.Dropdown(
        label="Tipo de Delito",
        border="outline",
        options=[
            ft.dropdown.Option("Robo con Fuerza"),
            ft.dropdown.Option("Seguridad Vial"),
            ft.dropdown.Option("Lesiones"),
        ],
    )

    txt_dni = ft.TextField(label="DNI/NIE", border="outline")
    txt_nombre = ft.TextField(label="Nombre Completo", border="outline")

    # --- BOTÓN ---
    btn_generar = ft.ElevatedButton(
        text="GENERAR Y GUARDAR",
        icon=ft.icons.SAVE,
        bgcolor="blue",
        color="white",
        on_click=generar_documento
    )

    # --- PESTAÑAS ---
    mis_tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(
                text="General",
                icon=ft.icons.DASHBOARD,
                content=ft.Column([
                    ft.Text("Datos Generales", size=20, weight="bold"),
                    txt_atestado, txt_fecha, dd_delito
                ], spacing=20)
            ),
            ft.Tab(
                text="Personas",
                icon=ft.icons.PEOPLE,
                content=ft.Column([
                    ft.Text("Datos Personales", size=20, weight="bold"),
                    txt_dni, txt_nombre, ft.Divider(), btn_generar
                ], spacing=20)
            ),
        ],
        expand=1,
    )

    page.add(mis_tabs)

ft.app(target=main)
