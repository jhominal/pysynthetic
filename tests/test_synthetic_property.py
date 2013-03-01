#-*- coding: utf-8 -*-
#
# Created on Dec 17, 2012
#
# @author: Younes JAAIDI
#
# $Id$
#

from contracts import ContractNotRespected
from synthetic import DuplicateMemberNameError, \
                      NamingConventionCamelCase, NamingConventionUnderscore, \
                      synthesizeProperty, synthesize_member, \
                      synthesizeProperty, synthesize_property, \
                      namingConvention, naming_convention
import contracts
import unittest

@synthesizeProperty('minimalistProperty')
@synthesizeProperty('propertyWithDefaultValue', default = "default")
@synthesizeProperty('customProperty',
                    privateMemberName = '_internalPrivateSecretMemberThatShouldNeverBeUsedOutsideThisClass')
class TestBasic(object):
    pass

# By the way, we try the 'naming_convention' decorator.
# This will test that when naming convention decorator will try to recreate accessors,
# it will not try to remove the setter as the member is 'read only'.
@naming_convention(NamingConventionCamelCase())
@synthesizeProperty('readOnlyProperty', readOnly = True)
class TestReadOnly(object):
    pass

@synthesizeProperty('propertyString', contract = str)
@synthesizeProperty('propertyStringList', contract = 'list(str)')
class TestContract(object):
    pass

@synthesizeProperty('propertyWithCustomGetterSetter')
@synthesizeProperty('propertyWithCustomGetter')
class TestCustomProperties(object):

    @property
    def propertyWithCustomGetterSetter(self):
        return 'property_with_custom_getter_setter_value'
    
    @propertyWithCustomGetterSetter.setter
    def propertyWithCustomGetterSetter(self, value):
        self._propertyWithCustomGetterSetter = 'property_with_custom_getter_setter_value'

    @property
    def propertyWithCustomGetter(self):
        return 'property_with_custom_getter_value'

class TestClass(object):
    pass

class TestSynthesizeProperty(unittest.TestCase):

    def setUp(self):
        contracts.enable_all()

    def testOK(self):
        instance = TestBasic()
        
        # Default default ;) member value is None.
        self.assertEqual(None, instance.minimalistProperty)
        
        # Default set and get test. 
        instance.minimalistProperty = 10
        self.assertEqual(10, instance.minimalistProperty)
        
        # Checking custom default value.
        self.assertEqual("default", instance.propertyWithDefaultValue)
        
        # Custom private member name.
        instance.customProperty = "newValue"
        self.assertFalse(hasattr(instance, '_customProperty'))
        self.assertEqual("newValue", instance._internalPrivateSecretMemberThatShouldNeverBeUsedOutsideThisClass)
        self.assertEqual("newValue", instance.customProperty)
   
    def testReadOnly(self):
        instance = TestReadOnly()
        
        self.assertTrue(hasattr(instance, 'readOnlyProperty'))
        
        with self.assertRaises(AttributeError):
            instance.readOnlyProperty = 10
    
    def testCustomAccessors(self):
        """If accessors are overriden, they should not be synthesized.
We also check that there's no bug if the naming convention is changed.
"""
        instance = TestCustomProperties()
        self.assertEqual(None, instance._propertyWithCustomGetterSetter)
        self.assertEqual(None, instance._propertyWithCustomGetter)

        # Testing custom setters.
        instance.propertyWithCustomGetterSetter = "placeholder"
#@todo:        instance.propertyWithCustomGetter = "value"
        
        self.assertEqual('property_with_custom_getter_setter_value', instance._propertyWithCustomGetterSetter)
#@todo:        self.assertEqual('value', instance._propertyWithCustomGetter)
        
        # Testing custom getters.
        instance = TestCustomProperties()
        self.assertEqual(None, instance._propertyWithCustomGetterSetter)
        self.assertEqual(None, instance._propertyWithCustomGetter)
        
        self.assertEqual('property_with_custom_getter_setter_value', instance.propertyWithCustomGetterSetter)
        self.assertEqual('property_with_custom_getter_value', instance.propertyWithCustomGetter)

    def testContract(self):
        instance = TestContract()
        
        # OK.
        instance.propertyString = "I love CamelCase!!!"
        instance.propertyStringList = ["a", "b"]
        
        # Not OK.
        with self.assertRaises(ContractNotRespected):
            instance.propertyString = 10
            
        with self.assertRaises(ContractNotRespected):
            instance.propertyStringList = ["a", 2]

        # Checking exception message.
        try:
            instance.propertyString = 10
            self.fail(u"Exception not raised.")
        except ContractNotRespected as e:
            self.assertEqual("""\
Expected type 'str', got 'int'.
checking: str   for value: Instance of int: 10   
Variables bound in inner context:
- propertyString: Instance of int: 10""", str(e))

    def testContractDisabled(self):
        instance = TestContract()

        contracts.disable_all()

        # No exception is raised
        instance.propertyString = 10
        instance.propertyStringList = ["a", 2]

    def testDuplicateMemberName(self):
        # Equivalent to:
        # @syntheticMember('member')
        # @syntheticMember('member')
        # class TestClass:
        #     pass
        
        ClassWithSynthesizedProperty = synthesizeProperty('property')(TestClass)
        self.assertRaises(DuplicateMemberNameError, synthesizeProperty('property'), ClassWithSynthesizedProperty)
