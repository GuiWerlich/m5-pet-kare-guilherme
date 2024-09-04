from rest_framework.views import APIView, Response, status
from rest_framework.pagination import PageNumberPagination
from .models import Pet
from groups.models import Group
from traits.models import Trait
from .serializers import PetSerializer, PetPutSerializer


class PetView(APIView, PageNumberPagination):

    def post(self, request):
        serializer = PetSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group_data = serializer.validated_data.pop('group')
        trait_list = serializer.validated_data.pop('traits')

        found_group = Group.objects.filter(scientific_name=group_data['scientific_name'])
        
        if found_group.exists():
            group = Group.objects.get(scientific_name=group_data['scientific_name'])    
        else:            
            group = Group.objects.create(**group_data)

        pet = Pet.objects.create(**serializer.validated_data, group=group)

        for trait in trait_list:
            found_trait = Trait.objects.filter(name__iexact=trait['name'])
            if found_trait.exists():
                trait = found_trait.first()
            else:
                trait = Trait.objects.create(**trait)

            pet.traits.add(trait)
        
        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def get(self, request, pet_id=None):

        if pet_id != None:
            found_pet = Pet.objects.filter(id=pet_id)

            if not found_pet.exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
                        
            pets = Pet.objects.get(id=pet_id)
            serializer = PetSerializer(pets)
            return Response(serializer.data)

        trait = request.query_params.get('trait', None)

        if trait:
            pets = Pet.objects.filter(traits__name__icontains=trait)   
            if not pets.exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)                        
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request, view=self)      
        serializer = PetSerializer(result_page, many=True)   

        return self.get_paginated_response(serializer.data)
    
    
    def patch(self, request, pet_id=None):
        if pet_id is not None:
            found_pet = Pet.objects.filter(id=pet_id)

            if not found_pet.exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PetPutSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated = serializer.validated_data

        pet = Pet.objects.get(id=pet_id)

        pet.name = validated.get('name', pet.name)
        pet.age = validated.get('age', pet.age)
        pet.weight = validated.get('weight', pet.weight)
        pet.sex = validated.get('sex', pet.sex)
        
        if 'group' in validated:
            group_data = validated['group']
            found_group = Group.objects.filter(scientific_name=group_data['scientific_name'])

            if found_group.exists():
                group = Group.objects.get(scientific_name=group_data['scientific_name'])
                pet.group = group
            else:
                group = Group.objects.create(**group_data)
                pet.group = group
            
            pet.group = group
            
        
        if 'trait' in validated:
            trait_list = validated['trait']
            trait_objects = []

            for trait_data in trait_list:
                found_trait = Trait.objects.filter(name__icontains=trait_data['name'])
                if found_trait.exists():
                        trait = Trait.objects.get(name__icontains=trait_data['name'])
                else:
                    trait = Trait.objects.create(**trait_data)
                
                trait_objects.append(trait)

            pet.traits.set(trait_objects)
        
        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def delete(self, request, pet_id=None):

        if pet_id != None:
            found_pet = Pet.objects.filter(id=pet_id)

            if not found_pet.exists():
                return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

            pet = Pet.objects.get(id=pet_id)
            pet.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)