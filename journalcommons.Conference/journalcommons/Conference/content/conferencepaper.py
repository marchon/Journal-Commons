"""Definition of the ConferencePaper content type
"""

from zope.interface import implements, directlyProvides
from Acquisition import aq_inner, aq_parent

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import atapi
from Products.Archetypes.utils import mapply  
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

# gcommons
from gcommons.Core.lib.relators import RelatorsMixin
from journalcommons.Conference import ConferenceMessageFactory as _
from journalcommons.Conference.interfaces import IConferencePaper
from journalcommons.Conference.config import PROJECTNAME

import logging
logger = logging.getLogger('jcommons.Conference.content.ConferencePaper')



#####################################
# Schema
ConferencePaperSchema = folder.ATFolderSchema.copy() + RelatorsMixin.schema.copy() + atapi.Schema((
    # -*- Your Archetypes field definitions here ... -*-
    atapi.StringField(
        name='specialRequirements',
        required=False,
        searchable=1,
        #default='',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Special Requirements"),
            description=_(u"Does your paper require any specific requirements? Type any special requirements here (such as Powerpoint, video equipment, etc)"),
        ),
    ),

    atapi.ReferenceField(
        name='refPanel',
        relationship = 'refPanel',
        required=False,
        multiValued = False,
        searchable=1,
        #TODO: this should be a proper permission, not generic one
        write_permission='Manage Portal',
        vocabulary = 'listAvailablePanels',
        enforceVocabulary = True,
        mutator = 'setPanelRef',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u"Session"),
            description=_(u"Choose a conference session from above if your paper is part of a session proposal. Leave blank otherwise."),
        ),
    ),
    
    # TEMPORARY FIX
    atapi.StringField(
        name='isPartPanel',
        required=False,
        searchable=1,
        #default='',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            visible = {'edit' : 'invisible', 'view' : 'invisible' },
            label=_(u"Part of Proposed Panel"),
            description=_(u"Is your paper part of a panel proposal? Fill in only if you or a colleage are submitting a panel as well, leave blank otherwise."),
        ),
    ),

    atapi.BooleanField('isPanel',
    	required = False,
    	languageIndependent = True,
    	widget = atapi.BooleanWidget(
                visible = {'edit' : 'invisible', 'view' : 'invisible' },
    	        label= _(u"Is this a panel?"),
    	        description = _(u"Consider this proposal a panel rather than a paper."),
    	),
    ),
))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.
def finalizeConferenceSchema(schema):
    schema['title'].storage = atapi.AnnotationStorage()
    schema['description'].storage = atapi.AnnotationStorage()
    schema['description'].required = True
    schema['description'].widget.label = _('Abstract')
    schema['description'].widget.description = _('A short summary of your article.')
    schema['subject'].storage = atapi.AnnotationStorage()
    schema['subject'].widget.label = _('Keywords')
    schema['subject'].widget.description  = _('Please select among the existing keywords or add new ones to describe the subjects of your submission.')

    
    # Hide this fields
    for field in ('effectiveDate', 'expirationDate',):
        schema[field].widget.visible = {'edit': 'invisible', 'view': 'invisible'}
    
    # Call ATContentTypes
    schemata.finalizeATCTSchema(
        schema,
        folderish=True,
        moveDiscussion=False
    )
    
    # Fix after ATContentTypes
    # Reorder
    schema.moveField('description', before='specialRequirements')
    schema.moveField('subject', after='description')
    # Schematas
    schema.changeSchemataForField('subject', 'default')
    return schema
    

class ConferencePaper(folder.ATFolder, RelatorsMixin):
    """A paper submitted to a conference"""
    implements(IConferencePaper)

    meta_type = "ConferencePaper"
    schema = finalizeConferenceSchema(ConferencePaperSchema)
    
    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    specialRequirements = atapi.ATFieldProperty('specialRequirements')

        
    # Vocabulary
    def listAvailablePanels(self):
        context = aq_inner(self)
        panels = context.aq_getAvailablePanels()
        list = atapi.DisplayList()
        list.add('0',"None, let Organizers decide")
        for panel in panels:
            list.add(panel['uid'], "%s, proposed by %s" % (panel['description'],panel['creator'])) 
        return list
    
    
    def setPanelRef(self, value, **kw):
        """
        a variation of default mutator from ClassGen.py
        with a special case
        """
        name = kw.get('field')
        """ Default Mutator """
        if kw.has_key('schema'):
            schema = kw['schema']
        else:
            schema = self.Schema()
            kw['schema'] = schema

        if value != '0':
            return schema[name].set(self, value, **kw)
        else:
            return schema[name].set(self, None, **kw)
        
        
    ###COMMON!
    def get_container(self):
        return self.getRefPanel()
    
    def get_item_subtype(self, name=False):
        return "Paper"
    
    def get_review_state(self):
        review_state = self.portal_workflow.getInfoFor(self, 'review_state');
        return review_state
    
    def get_state_comments(self):
        review_state = self.get_review_state()
        if review_state == 'draft':
            return "You need to finish editing your paper and submit it to editors for evaluation"
        elif review_state == 'eb_draft':
            return "Your paper is awaiting evaluation by editors"
        else:
            return review_state
    
    def get_drafts(self):
        brains = self.listFolderContents(contentFilter={"portal_type" : "File"})
        #brains = self.portal_catalog({'portal_type':'File',
        #                     'path':'/'.join(self.context.getPhysicalPath()),
        #                     'sort_on':'sortable_title'})
        #groups = [i.getObject() for i in brains]
        return brains
        
    def get_no_drafts(self):
        return len( self.get_drafts() )
    

    # Migration code
    def migrate_to_panel(self):
	"""
	temp
	"""
	parent = aq_parent(aq_inner(self))
	htmltext = self.description
	self.migrate_author()
	#htmltext = htmltext.replace("\n", "<br/>")
	fldid = parent.invokeFactory('ConferenceEvent', 'panel_%s' % self.getId(), title = self.title,
                        description=self.description, text=htmltext, creators=self.creators, 
                        primaryAuthor=self.getPrimaryAuthor(), unregisteredRelators=self.getUnregisteredRelators() )
        obj = parent[fldid]
        obj.changeOwnership( self.getOwner(), 0 )
        return self.listCreators()

    def migrate_author(self):
    	"""
    	temp
    	"""
    	extra = []
    	for name in self.getUnconfirmedExtraAuthors():
    	    extra.append(name)
    
    	self.setUnregisteredRelators( extra )
    	return self.getUnconfirmedExtraAuthors()

atapi.registerType(ConferencePaper, PROJECTNAME)
