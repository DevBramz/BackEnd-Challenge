import csv
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Order

# class TitleSearchMixin:
# def get_queryset(self):
# # Fetch the queryset from the parent's get_queryset
# queryset = super().get_queryset()
# # Get the q GET parameter
# q = self.request.GET.get('q')
# if q:
# 156


# def get_data_for_export(self, request, queryset, *args, **kwargs):
#         export_form = kwargs.pop('export_form', None)
#         return self.choose_export_resource_class(export_form)\
#             (**self.get_export_resource_kwargs(request, *args, **kwargs))\
#             .export(queryset, *args, **kwargs)

#     def get_export_filename(self, file_format):
#         date_str = now().strftime('%Y-%m-%d')
#         filename = "%s-%s.%s" % (self.model.__name__,
#                                  date_str,
#                                  file_format.get_extension())
#         return filename


class ExportViewMixin:
    """
    EXport orders mixin
    """
    qs = None
    
    def export(self,qs):
        
        """

        Returns a JSON response, transforming 'context' to make the export data

        """
        
        model = Order
        # date_str = now().strftime('%Y-%m-%d')
        resp = HttpResponse(content_type="text/csv")
        resp["Content-Disposition"] = "attachment; filename=%s.csv" % (
            slugify(model.__name__)
        )
        writer = csv.writer(resp)
        # Write headers to CSV file
        headers = [
            "code",
            "category",
        ]
        # opts = queryset.model._meta
        # field_names = [field.name for field in opts.fields]
        for field in model._meta.fields:
            if field.name not in ("added", "edited", "id", "code", "category"):
                headers.append(field.name)

        writer.writerow(headers)
        # Write data to CSV file
        for obj in qs:
            row = []
            for field in headers:
                if field in headers:
                    val = getattr(obj, field)
                    if callable(val):
                        val = val()
                    row.append(val)
            writer.writerow(row)
        # Return CSV file to browser as download
        if resp:

            return resp
        else:
            return Response(
                {"status": "failed", "message": "export failed"},
                status=status.HTTP_410_GONE,
            )


# def export(qs, fields=None):
#     model = qs.model
#     response = HttpResponse(mimetype='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(model.__name__)
#     writer = csv.writer(response)
#     # Write headers to CSV file
#     if fields:
#         headers = fields
#     else:
#         headers = []
#         for field in model._meta.fields:
#             headers.append(field.name)
#     writer.writerow(headers)
#     # Write data to CSV file
#     for obj in qs:
#         row = []
#         for field in headers:
#             if field in headers:
#                 val = getattr(obj, field)
#                 if callable(val):
#                     val = val()
#                 row.append(val)
#         writer.writerow(row)
#     # Return CSV file to browser as download
#     return response
