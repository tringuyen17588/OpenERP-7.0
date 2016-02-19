# -*- coding: utf-8 -*-..,
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Crea8s (http://www.crea8s.com) All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  
##############################################################################

from openerp.osv import fields, osv

class crea8s_vec_type_of_proposal(osv.osv):
    _name = "crea8s.vec.type.of.proposal"
    _description = 'crea8s_vec_type_of_proposal...'
    _columns = {
        'name': fields.char('Type of Proposal', size=30), 
    }
    
crea8s_vec_type_of_proposal()

class crea8s_vec_type_of_proposal_package(osv.osv):
    _name = "crea8s.vec.type.of.proposal.package"
    _description = 'crea8s_vec_type_of_proposal_package...'
    _columns = {
        'name': fields.char('Type of Proposal Package', size=30), 
    }
    
crea8s_vec_type_of_proposal_package()

class crea8s_vec_project(osv.osv):
    _name = "crea8s.vec.project"
    _description = 'crea8s_vec_project...'
    _columns = {
        'ref': fields.char('Project Ref', size=30), 
        'name': fields.char('Project Name', size=100), 
    }
    
crea8s_vec_project()