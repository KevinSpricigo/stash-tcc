import flet as ft
from banco.conexao2 import supabase
from datetime import datetime

async def pagamentos(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return

    servico_data = page.session_data.get('servico_data')
    profissional_data = page.session_data.get('profissional_data')
    horas_selecionadas = int(page.session_data.get('horas_selecionadas', '1'))
    valor_hora = float(page.session_data.get('valor_hora', 0))
    
    if not servico_data or not profissional_data:
        page.go('/')
        return

    valor_total = valor_hora * horas_selecionadas
    selected_payment = None

    def pagamento_selecionado(e):
        nonlocal selected_payment
        selected_payment = e.control.value

    async def processar_pagamento(e):
        try:
            if not selected_payment:
                print("Erro: Selecione um método de pagamento")
                return

            pessoa_servico = supabase.table('pessoa_servico').insert({
                'id_pessoa': page.session_data.get('user_id'),
                'id_servico': servico_data['id_servico'],
                'data': datetime.now().isoformat()
            }).execute()

            id_pessoa_servico = pessoa_servico.data[0]['id_pessoa_servico']

            ordem = supabase.table('ordens').insert({
                'id_pessoa': page.session_data.get('user_id'),
                'id_servico': servico_data['id_servico'],
                'id_profissional': profissional_data['id_profissional'],
                'data_pedido': datetime.now().isoformat(),
                'status': 'pendente',
                'id_pessoa_servico': id_pessoa_servico
            }).execute()

            pagamento = supabase.table('pagamentos').insert({
                'data': datetime.now().isoformat(),
                'modo': selected_payment,
                'valor': valor_total,
                'id_pessoa_servico': id_pessoa_servico
            }).execute()

            page.go('/conclusao-servico')

        except Exception as e:
            print(f"Erro ao processar pagamento: {e}")

    components = [
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        ft.CircleAvatar(
                            foreground_image_url=profissional_data.get('avatar_url') if profissional_data.get('avatar_url') else None,
                            content=ft.Icon(ft.icons.PERSON) if not profissional_data.get('avatar_url') else None,
                            radius=35
                        ),
                        padding=ft.padding.only(top=0, left=10, right=10, bottom=0)
                    ),
                    ft.Column([
                        ft.Row([ft.Container(
                            content=ft.Text(
                                value=f"{profissional_data['nome']} {profissional_data['sobrenome']}",
                                size=16,
                                color='black',
                                font_family='Poppins Medium'
                            ),
                            expand=True
                        )], width=200),
                        ft.Row([ft.Container(
                            ft.Text(
                                value=f"{servico_data['nome']} ({horas_selecionadas}h)",
                                color='black',
                                size=14,
                                font_family='Poppins Regular'
                            ),
                            expand=True
                        )]),
                        ft.Row([
                            ft.Container(width=170),
                            ft.Container(
                                content=ft.Text(
                                    value=f"R$ {valor_total:.2f}",
                                    color='black',
                                    size=16,
                                    font_family='Poppins Regular'
                                ),
                            )
                        ])
                    ]),
                ],
            ),
            padding=ft.padding.only(bottom=0)
        ),
        ft.Divider(),
        ft.Container(
            content=ft.Text("Método de Pagamento", size=16, font_family='Poppins Medium', color="black"),
            margin=ft.margin.only(left=10, right=10)
        ),
        ft.Container(
            content=ft.RadioGroup(
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Icon(ft.icons.PIX, color=ft.colors.GREEN),
                            ft.Text("Pix", size=16, color="black"),
                            ft.Radio(fill_color=ft.colors.GREEN, value='pix')
                        ]),
                        ft.Row(controls=[
                            ft.Icon(ft.icons.ATTACH_MONEY, color=ft.colors.GREEN),
                            ft.Text("Dinheiro", size=16, color="black"),
                            ft.Radio(fill_color=ft.colors.GREEN, value='dinheiro')
                        ]),
                    ],
                    spacing=10
                ),
                on_change=pagamento_selecionado
            ),
            margin=ft.margin.only(left=10, right=10)
        ),
        ft.Container(
            ft.ElevatedButton(
                content=ft.Text(
                    value='Pagar',
                    size=16,
                    color='#FFFFFF'
                ),
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=15),
                    bgcolor='#2ECC71'
                ),
                width=225,
                height=42,
                on_click=processar_pagamento
            ),
            alignment=ft.alignment.center,
            margin=ft.margin.only(top=20, left=20, right=20)
        )
    ]

    page.add(*components)