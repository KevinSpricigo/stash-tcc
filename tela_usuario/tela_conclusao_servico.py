import flet as ft
from banco.conexao2 import supabase
from datetime import datetime

async def conclusao_servico(page: ft.Page):
    if not hasattr(page, 'session_data') or not page.session_data.get('user_id'):
        page.go('/login')
        return
    
    user_id = page.session_data.get('user_id')
    if not user_id:
        page.go('/login')
        return
    
    page.bgcolor = '#FFFFFF'
    page.scroll = ft.ScrollMode.AUTO

    def ir_avaliar(e, ordem_id, servico_id):
        page.session_data['ordem_id'] = ordem_id
        page.session_data['servico_selecionado'] = servico_id
        page.go('/avaliar-servico')

    try:
        ordens = supabase.table('ordens')\
            .select('*, servicos(*), profissionais(*)')\
            .eq('id_pessoa', user_id)\
            .order('data_pedido', desc=True)\
            .execute()

        if not ordens.data:
            page.add(
                ft.Container(
                    content=ft.Text(
                        "Nenhum serviço contratado ainda.",
                        size=16,
                        color='black',
                        text_align=ft.TextAlign.CENTER
                    ),
                    margin=ft.margin.only(top=50),
                    alignment=ft.alignment.center
                )
            )
            return

        for ordem in ordens.data:
            servico = ordem['servicos']
            profissional = ordem['profissionais']
            
            servico_aceito = ordem.get('status') == 'aceito'

            avaliacoes = supabase.table('avaliacoes')\
                .select('id_avaliacao')\
                .eq('id_servico', servico['id_servico'])\
                .eq('id_pessoa', user_id)\
                .eq('id_ordem', ordem['id_ordem'])\
                .execute()

            ja_avaliado = len(avaliacoes.data) > 0

            pagamento = None
            if ordem.get('id_pessoa_servico'):
                pagamento = supabase.table('pagamentos')\
                    .select('valor')\
                    .eq('id_pessoa_servico', ordem['id_pessoa_servico'])\
                    .execute()

            valor_total = pagamento.data[0]['valor'] if pagamento and pagamento.data else servico['valor']
            horas = int(round(valor_total / servico['valor'])) if servico['valor'] > 0 else 1

            status_text = ""
            if ordem.get('status') == 'negado':
                status_text = "Negado pelo profissional"
            elif not servico_aceito:
                status_text = "Aguardando profissional"

            if ordem.get('status') == 'negado':
                texto_botao = "Negado"
                cor_botao = ft.colors.RED
                botao_desabilitado = True
            else:
                texto_botao = "Avaliado" if ja_avaliado else "Pendente" if not servico_aceito else "Avaliar"
                cor_botao = ft.colors.GREY if ja_avaliado or not servico_aceito else '#2ECC71'
                botao_desabilitado = ja_avaliado or not servico_aceito

            status_column = [
                ft.Text(
                    value=f"{profissional['nome']} {profissional['sobrenome']}", 
                    size=16, 
                    font_family='Poppins Medium', 
                    color=ft.colors.BLACK
                ),
                ft.Text(
                    value=servico['nome'], 
                    size=14, 
                    font_family='Poppins Regular',
                    color=ft.colors.GREY
                )
            ]

            if status_text:
                status_column.append(
                    ft.Text(
                        value=status_text,
                        size=12,
                        font_family='Poppins Regular',
                        color=ft.colors.RED if ordem.get('status') == 'negado' else ft.colors.GREY
                    )
                )

            card = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.CircleAvatar(
                                    foreground_image_url=profissional.get('avatar_url') if profissional.get('avatar_url') else None,
                                    content=ft.Icon(ft.icons.PERSON) if not profissional.get('avatar_url') else None,
                                    radius=30
                                ),
                                ft.Column(
                                    controls=status_column,
                                    spacing=5
                                ),
                            ],
                            spacing=20
                        ),
                        padding=ft.padding.symmetric(vertical=20)
                    ),
                    ft.Row(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(
                                        value=f"R$ {valor_total:.2f}", 
                                        size=16, 
                                        font_family='Poppins Bold', 
                                        color='#2ECC71'
                                    ),
                                    ft.VerticalDivider(
                                        color=ft.colors.GREY_400, 
                                        width=20, 
                                        thickness=1
                                    ),
                                    ft.Text(
                                        value=f"{horas} horas", 
                                        size=16, 
                                        font_family='Poppins Regular',
                                        color=ft.colors.GREY
                                    ),
                                ],
                                spacing=5
                            ),
                            ft.ElevatedButton(
                                text=texto_botao,
                                bgcolor=cor_botao,
                                color=ft.colors.WHITE,
                                width=110,
                                height=30,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=None if botao_desabilitado else lambda e, o=ordem['id_ordem'], s=servico['id_servico']: ir_avaliar(e, o, s),
                                disabled=botao_desabilitado
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ]),
                padding=ft.padding.all(10),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                margin=ft.margin.only(bottom=10, left=10, right=10)
            )

            page.add(card)
            
    except Exception as e:
        print(f"Erro ao carregar serviços: {e}")
        page.add(
            ft.Text(
                f"Erro ao carregar serviços: {str(e)}",
                color="red",
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        )