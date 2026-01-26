from django import forms
from .models import Rubro, Movimiento, IngresoAgregado, OrganoEjecutor, TipoIngreso, RubroGasto, MovimientoGasto


class OrganoEjecutorForm(forms.ModelForm):
    """Formulario para Organos Ejecutores"""
    class Meta:
        model = OrganoEjecutor
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class IngresoAgregadoForm(forms.ModelForm):
    """Formulario para Ingresos Agregados (Fuentes)"""
    class Meta:
        model = IngresoAgregado
        fields = ['codigo', 'nombre', 'descripcion', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ICLD, SGP'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Alias para compatibilidad
FuenteFinanciacionForm = IngresoAgregadoForm


class RubroForm(forms.ModelForm):
    """Formulario para Rubros Presupuestales"""
    class Meta:
        model = Rubro
        fields = ['codigo', 'nombre', 'nivel', 'organo_ejecutor', 'ingreso_agregado',
                  'clase_ingreso', 'tipo_ingreso', 'codigo_fuente', 'es_totalizador', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Codigo presupuestal'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Concepto del ingreso'}),
            'nivel': forms.Select(attrs={'class': 'form-select'}),
            'organo_ejecutor': forms.Select(attrs={'class': 'form-select'}),
            'ingreso_agregado': forms.Select(attrs={'class': 'form-select'}),
            'clase_ingreso': forms.Select(attrs={'class': 'form-select'}),
            'tipo_ingreso': forms.Select(attrs={'class': 'form-select'}),
            'codigo_fuente': forms.TextInput(attrs={'class': 'form-control'}),
            'es_totalizador': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class MovimientoForm(forms.ModelForm):
    """Formulario para Movimientos - Version optimizada con AJAX"""
    TIPO_CHOICES_SIMPLE = [
        ('INICIAL', 'Presupuesto Inicial'),
        ('ADICION', 'Adicion'),
        ('REDUCCION', 'Reduccion'),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES_SIMPLE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Campo de texto para busqueda AJAX en lugar de Select con todos los rubros
    rubro = forms.ModelChoiceField(
        queryset=Rubro.objects.none(),  # Vacio inicialmente
        widget=forms.Select(attrs={
            'class': 'form-select rubro-select',
            'data-ajax-url': '/app/api/rubros/buscar/'
        })
    )

    class Meta:
        model = Movimiento
        fields = ['rubro', 'fecha', 'tipo', 'documento_soporte', 'valor', 'observaciones']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'documento_soporte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ordenanza 001 de 2026'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay instancia o datos iniciales, cargar solo ese rubro
        if self.instance and self.instance.pk:
            self.fields['rubro'].queryset = Rubro.objects.filter(pk=self.instance.rubro_id)
        elif self.data.get('rubro'):
            self.fields['rubro'].queryset = Rubro.objects.filter(pk=self.data.get('rubro'))
        elif self.initial.get('rubro'):
            self.fields['rubro'].queryset = Rubro.objects.filter(pk=self.initial.get('rubro'))


class TrasladoForm(forms.Form):
    """Formulario para Traslados entre rubros - Version optimizada"""
    rubro_origen = forms.ModelChoiceField(
        queryset=Rubro.objects.none(),
        label="Rubro Origen (Debito)",
        widget=forms.Select(attrs={
            'class': 'form-select rubro-select',
            'data-ajax-url': '/app/api/rubros/buscar/'
        })
    )
    rubro_destino = forms.ModelChoiceField(
        queryset=Rubro.objects.none(),
        label="Rubro Destino (Credito)",
        widget=forms.Select(attrs={
            'class': 'form-select rubro-select',
            'data-ajax-url': '/app/api/rubros/buscar/'
        })
    )
    fecha = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    documento_soporte = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Decreto 123 de 2026'})
    )
    valor = forms.DecimalField(
        max_digits=20,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0.01'})
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay datos POST, cargar esos rubros especificos
        if self.data.get('rubro_origen'):
            self.fields['rubro_origen'].queryset = Rubro.objects.filter(pk=self.data.get('rubro_origen'))
        if self.data.get('rubro_destino'):
            self.fields['rubro_destino'].queryset = Rubro.objects.filter(pk=self.data.get('rubro_destino'))

    def clean(self):
        cleaned_data = super().clean()
        origen = cleaned_data.get('rubro_origen')
        destino = cleaned_data.get('rubro_destino')
        if origen and destino and origen == destino:
            raise forms.ValidationError('El rubro origen y destino no pueden ser el mismo.')
        return cleaned_data


class AnularMovimientoForm(forms.Form):
    """Formulario para anular un movimiento"""
    motivo = forms.CharField(
        label="Motivo de Anulacion",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Indique el motivo de la anulacion',
            'required': True
        })
    )


# ==========================================
# FORMULARIOS PLAN FINANCIERO GASTOS
# ==========================================

class MovimientoGastoForm(forms.ModelForm):
    """Formulario para Movimientos de Gastos"""
    TIPO_CHOICES = [
        ('INICIAL', 'Presupuesto Inicial'),
        ('ADICION', 'Adicion'),
        ('REDUCCION', 'Reduccion'),
        ('CREDITO', 'Credito'),
        ('CONTRACREDITO', 'Contracredito'),
    ]

    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = MovimientoGasto
        fields = ['rubro', 'fecha', 'tipo', 'documento_soporte', 'valor', 'observaciones']
        widgets = {
            'rubro': forms.Select(attrs={'class': 'form-select'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'documento_soporte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ordenanza 001 de 2026'
            }),
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01'
            }),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rubro'].queryset = RubroGasto.objects.filter(activo=True)
