# Things to test:

# Substituting replaces all items
# Assigning the tag again actually adds the substitute

# Selecting a disabled tag generates an error
# flag to fail quietly? just doesn't assign it and doesn't generate an error
from django.test import TestCase

from simpleapp.models import SimpleText
from concepts.models import Concept

class SubstitutionTestCase(TestCase):
    def test_substitution(self):
        f = SimpleText.objects.create(name="Good Food")
        f.concepts.add("red", "crunchy", "smooth", "smoothy")
        g = SimpleText.objects.create(name="Bad Food")
        g.concepts.add("red", "crunchy",)
        
        c = Concept.objects.get(name="smoothy")
        r = Concept.objects.get(name="smooth")
        c.substitute = r
        c.save()
        
        # Items were moved to substitute
        self.assertEqual(c.items.count(), 0)
        self.assertEqual(f.concepts.count(), 3)
        
        # Adding it back doesn't do anything because substitute is there
        f.concepts.add("smoothy")
        self.assertEqual(f.concepts.count(), 3)
        
        # Adding it to a new item adds the substitute
        g.concepts.add("smoothy")
        self.assertEqual(g.concepts.count(), 3)
        assert(r in g.concepts.all())
    
    def test_enable(self):
        f = SimpleText.objects.create(name="Good Food")
        f.concepts.add("red", "crunchy", "smooth", "smoothy")
        
        bad_tag = Concept.objects.get(name="smoothy")
        bad_tag.enabled=False
        bad_tag.save()
        
        self.assertEqual(f.concepts.count(), 3)
        
        f.concepts.add("smoothy")
        self.assertEqual(f.concepts.count(), 3)
        print f.concepts.all()