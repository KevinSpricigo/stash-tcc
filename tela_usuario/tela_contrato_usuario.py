import flet as ft
from banco.conexao2 import supabase
from datetime import datetime

async def contratar(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return
    
    servico_id = page.session_data.get("servico_selecionado")
    if not servico_id:
        page.go('/')
        return

    page.bgcolor = '#FFFFFF'
    page.scroll = ft.ScrollMode.AUTO

    try:
        servico = supabase.table('servicos')\
            .select('*')\
            .eq('id_servico', servico_id)\
            .execute()
            
        if not servico.data:
            raise Exception("Serviço não encontrado")
            
        servico_data = servico.data[0]

        profissional = supabase.table('profissionais')\
            .select('*')\
            .eq('id_profissional', servico_data['id_profissional'])\
            .execute()
            
        if not profissional.data:
            raise Exception("Profissional não encontrado")
            
        profissional_data = profissional.data[0]

        page.session_data['servico_data'] = servico_data
        page.session_data['profissional_data'] = profissional_data
        page.session_data['horas_selecionadas'] = "1"
        valor_hora = float(servico_data['valor'])
        page.session_data['valor_hora'] = valor_hora

        preco_ref = ft.Ref[ft.Text]()
        radio_group = ft.Ref[ft.RadioGroup]()

        def on_horas_change(e):
            selected_value = radio_group.current.value
            horas = int(selected_value)
            page.session_data['horas_selecionadas'] = selected_value
            novo_valor = valor_hora * horas
            preco_ref.current.value = f"R$ {novo_valor:.2f}"
            page.update()

        components = [
            ft.Container(
                ft.CircleAvatar(
                    foreground_image_url=profissional_data.get('avatar_url') if profissional_data.get('avatar_url') else None,
                    content=ft.Icon(ft.icons.PERSON) if not profissional_data.get('avatar_url') else None,
                    radius=30,
                    scale=1.5
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=225),
            ),
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        value=f"{profissional_data['nome']} {profissional_data['sobrenome']}", 
                        color="black", 
                        weight="bold", 
                        size=20
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(top=10)
            ),
            ft.Container(
                content=ft.Row([
                    ft.Text(
                        value=f"R$ {valor_hora:.2f}",
                        color="green",
                        text_align='center',
                        size=20,
                        ref=preco_ref
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
                ),
                padding=ft.padding.only(top=0)
            ),
            ft.RadioGroup(
                content=ft.Row([
                    ft.Radio(value="1", label="1h", fill_color='#2ECC71', label_style=ft.TextStyle(color='black')),
                    ft.Radio(value="2", label="2h", fill_color='#2ECC71', label_style=ft.TextStyle(color='black')),
                    ft.Radio(value="3", label="3h", fill_color='#2ECC71', label_style=ft.TextStyle(color='black'))
                ], alignment=ft.MainAxisAlignment.CENTER),
                on_change=on_horas_change,
                value="1",
                ref=radio_group
            ),
            ft.Container(
                ft.ElevatedButton(
                    content=ft.Text(
                        value='Contratar',
                        size=16,
                        color='#FFFFFF',
                    ),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=32),
                        bgcolor='#2ECC71'
                    ),
                    width=192,
                    height=50,
                    on_click=lambda _: page.go('/pagamento-servico')
                ),
                alignment=ft.alignment.center,
                padding=ft.padding.only(top=20, left=20, right=20)
            )
        ]

        page.add(*components)

    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        page.add(
            ft.Text(
                f"Erro ao carregar dados: {str(e)}",
                color="red",
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        )